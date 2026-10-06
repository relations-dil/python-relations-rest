# Changelog

All notable changes to python-relations-rest are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

Shipping as 0.5.3, with relations-dil 0.6.16.

### Added
- Tests for a parent key stored in a dict field (`child_inject` in relations-dil 0.6.16): it goes to the server by name and comes back, and creating, counting, retrieving, filtering, updating, clearing and deleting through it work against a relations-restx API.

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
