import unittest
import unittest.mock

import http.server
import os
import shutil
import ssl
import subprocess
import tempfile
import threading

import relations_rest

class Seen(http.server.BaseHTTPRequestHandler):
    """
    Answers with the common name of the client certificate it was given, keeping the connection alive
    """

    protocol_version = "HTTP/1.1"

    def do_GET(self):

        body = dict(item[0] for item in self.connection.getpeercert()["subject"])["commonName"].encode()

        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass

@unittest.skipUnless(shutil.which("openssl"), "needs the openssl command to make certificates")
class TestCertificates(unittest.TestCase):
    """
    What a Source does when the certificates it was given are renewed on disk, which is what cert-manager
    and Kubernetes do to a mounted Secret: the files change, the paths stay.

    The answer, so apps know the rule: a Source reads its client certificate and its trusted CA from the files
    each time it opens a connection, so a renewal is used on the next connection. A connection that is already
    open keeps what it was opened with, so a renewal is used only once that connection is closed
    (`source.session.close()`, or the server closing it).
    """

    def run_openssl(self, command):

        subprocess.run(command, shell=True, cwd=self.pki, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def authority(self, name):

        self.run_openssl(f"openssl req -x509 -newkey rsa:2048 -nodes -keyout {name}.key -out {name}.crt -days 2 -subj /CN={name}")

    def certificate(self, name, authority, server=False):

        self.run_openssl(f"openssl req -newkey rsa:2048 -nodes -keyout {name}.key -out {name}.csr -subj /CN={name}")

        extensions = ""

        if server:
            with open(os.path.join(self.pki, f"{name}.ext"), "w", encoding="utf-8") as extension_file:
                extension_file.write("subjectAltName=DNS:localhost")
            extensions = f"-extfile {name}.ext"

        self.run_openssl(f"openssl x509 -req -in {name}.csr -CA {authority}.crt -CAkey {authority}.key -CAcreateserial -out {name}.crt -days 2 {extensions}")

    def copy(self, source, destination):

        for extension in ["crt", "key"]:
            shutil.copy(os.path.join(self.pki, f"{source}.{extension}"), os.path.join(self.pki, f"{destination}.{extension}"))

    def setUp(self):

        self.directory = tempfile.TemporaryDirectory() # pylint: disable=consider-using-with
        self.addCleanup(self.directory.cleanup)
        self.pki = self.directory.name

        self.authority("old")
        self.authority("new")
        self.certificate("server", "old", server=True)
        self.certificate("server_new", "new", server=True)
        self.certificate("client_old", "old")
        self.certificate("client_new", "old")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(os.path.join(self.pki, "server.crt"), os.path.join(self.pki, "server.key"))
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(os.path.join(self.pki, "old.crt"))

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Seen)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)

        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()

        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

        # what the Source is given: the files a mounted Secret would be, which are renewed by replacing their contents

        self.copy("client_old", "client")
        shutil.copy(os.path.join(self.pki, "old.crt"), os.path.join(self.pki, "trust.crt"))

        self.source = relations_rest.Source(
            "certificates",
            f"https://localhost:{self.server.server_address[1]}/",
            cert=(os.path.join(self.pki, "client.crt"), os.path.join(self.pki, "client.key")),
            verify=os.path.join(self.pki, "trust.crt")
        )
        self.addCleanup(self.source.session.close)

    def seen(self):

        return self.source.session.get(self.source.url).text

    def test_client_certificate(self):

        self.assertEqual(self.seen(), "client_old")

        self.copy("client_new", "client")

        # the connection is still open, so it is still the old certificate

        self.assertEqual(self.seen(), "client_old")

        # the next connection reads the files again

        self.source.session.close()

        self.assertEqual(self.seen(), "client_new")

    def test_trusted_authority(self):

        self.assertEqual(self.seen(), "client_old")

        # the server is renewed from a new authority the Source doesn't trust yet

        self.server.socket.context.load_cert_chain(os.path.join(self.pki, "server_new.crt"), os.path.join(self.pki, "server_new.key"))
        self.source.session.close()

        with self.assertRaises(Exception) as caught:
            self.seen()

        self.assertIn("SSLError", type(caught.exception).__name__)

        # the authority it trusts is renewed on disk, and the next connection reads it

        shutil.copy(os.path.join(self.pki, "new.crt"), os.path.join(self.pki, "trust.crt"))

        self.assertEqual(self.seen(), "client_old")
