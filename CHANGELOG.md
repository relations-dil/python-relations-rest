# Changelog

All notable changes to python-relations-rest are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [0.5.6] - 2026-10-29

### Added
- How a Source treats renewed certificates, proven by `test/test_certificates.py` and written up in the README: a client certificate and a trusted CA given as `cert` and `verify` paths are read again for each new connection, so a renewal is used from the next connection, and an open connection keeps the old one until it closes. The test image has `openssl` for it (relations-dil/python-relations-rest#20).
- Jenkins releases on a merge to `main`: a `release` stage (only on `main`) runs `make release`, which does nothing for a version that is already released and otherwise does the test release, the release and the tag. It pushes the tag with the `github` credential, as Leroy Jenkins, one build at a time, with a two hour timeout (relations-dil/python-relations#80). The package builds run in a copy with only the files they use mounted read-only, so nothing root-owned is left in the workspace, and `make tag` stops on a failure instead of ignoring it. The release scripts work with the older git on the Jenkins host.
- `make help` lists every target with what it does (each target has a `## description` after it), and is what a bare `make` runs.
- Release tooling, the same as relations-dil's (relations-dil/python-relations#77): `make new` starts a release, `make version` sets the version, `make release-check` says where a release is up to and what would stop it, `make release` does what's left (checks, TestPyPI and a clean install from it, PyPI, the tag), `make dist-check` builds and checks the distributions, and `make test-release` tests the scripts against a throwaway repo and fake indexes. The work is in `scripts/`.

### Changed
- `make release-check` and `make release` don't run `build`, `test`, `lint` and `setup` again: the Jenkins stages have just run them before the release stage, so it was the same work twice. Run them yourself before checking by hand, as `make release-check` is only the checks and `dist-check` now (relations-dil/python-relations#90).
- Every `docker run` in the `Makefile` uses `--rm`, and a replaced database container is removed with its volume (`docker rm --force -v`), so builds and test runs leave no stopped containers or volumes behind.
- `testpypi` and `pypi` run in the current `python` image with `build` and `twine` installed on the fly, so the custom `gaf3/pypi` image is no longer used.

Shipping as 0.5.3, with relations-dil 0.6.16.

### Added
- Tests for a parent key stored in a dict field (`child_inject` in relations-dil 0.6.16): it goes to the server by name and comes back, and creating, counting, retrieving, filtering, updating, clearing and deleting through it work against a relations-restx API.

## [0.5.5] - 2026-10-14

### Changed
- An error response is the error the other sources raise: a 404 is `relations.NotFoundError`, a 409 is `relations.UniqueError`, any other 4xx or 5xx stays a `relations.ModelError`. The message is the API's, as before.
- "none retrieved" and "more than one retrieved" are `relations.NotFoundError` and `relations.MultipleError` (same messages, still `ModelError`s). A 409 for a duplicate comes from a server running relations-restx 0.6.7 or later. Needs relations-dil 0.6.19 (relations-dil/python-relations#78).

## [0.5.4] - 2026-10-14

### Fixed
- A readonly field, the string id from relations-dil 0.6.18, is never sent in an update or a mass update (`update_field`, `field_mass`), so a local change to it can't be PATCHed.
- The id in the update URL is quoted (`urllib.parse.quote`, nothing left unescaped), so an id with a space, `?` or `#` addresses the right record. A `/` in an id is still not routed by Flask's default converter, so keep it out of ids.
- Needs relations-dil 0.6.18.

## [0.5.2] - 2026-06-08

- `Source.count` and `Source.retrieve` now send sibling-attribute tie filters (such as `bro__name`) to the API through a new `filter_ties` method.
- Bumped `relations-restx` to 0.6.4 and `relations-dil` to 0.6.15, and installed git in the Dockerfile.

## [0.5.1] - 2026-06-07

- `Source` now loads many-to-many tie ids that the API returns inline onto retrieved models through a new `retrieve_ties` method, for both single and multiple results.
- Bumped `relations-restx` to 0.6.3 and `relations-dil` to 0.6.14, and changed the setup step to `pip install .`.

## [0.5.0] - 2022-12-10

- Bumped the `relations-restx` requirement to 0.6.2 and the `relations-dil` requirement to 0.6.12, with the version now coming from the `VERSION` file.

## [0.4.0] - 2022-09-10

- Collapsed the `relations_rest` package into a single `lib/relations_rest.py` module; `Source` is still imported from `relations_rest`.
- Moved the version into a `VERSION` file and simplified the packaging and test layout.

## [0.3.0] - 2022-08-10

- Prepared the package for PyPI with a `LICENSE.txt`, a `PYPI.md` description, and `testpypi` and `pypi` Makefile targets.
- Removed the git-based installs from the Dockerfile and setup step.

## [0.2.0] - 2022-05-01

- Removed the bundled unittest helper in favor of the shared Relations unittests and reduced dependencies.
- Updated the README.

## [0.1.0] - 2022-04-30

- Initial release with `relations_rest.Source`, a Relations `Source` that uses a REST API as its backend through a `requests` session, with create, retrieve, count, update and delete calls and handling of the API's `overflow` flag and error messages.
- Included a unittest helper module with tests, Dockerfile, Jenkinsfile and Makefile.
