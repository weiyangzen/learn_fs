# sources/distributed-fs/tahoe-lafs/tox.ini

## Purpose
This file defines Tahoe-LAFS test, type-check, lint, docs, release-note, integration, and packaging tox environments and maps GitHub Actions Python versions to tox jobs.

## Important APIs, Types, and Functions
`[gh-actions]` maps Python 3.9-3.12 and PyPy 3.9 to coverage or PyPy jobs. `[pytest] twisted = 1` enables Twisted pytest integration. `[tox]` sets envlist and `minversion = 4`. The default `[testenv]` installs Tahoe with `testenv` and `test` extras, runs `pip freeze`, `tahoe --version`, stdout encoding inspection, and Twisted Trial with optional coverage. Named environments include `integration`, `codechecks`, `typechecks`, `draftnews`, `news`, `deprecations`, `upcoming-deprecations`, `docs`, `pyinstaller`, and `tarballs`.

## Control Flow
Tox creates isolated environments, installs deps/extras, sets pass-through environment variables, then executes commands. Coverage jobs switch Trial invocation to `coverage run`, combine data, and emit XML. `codechecks` runs ruff, Tahoe coding tools, and Towncrier fragment checks. `typechecks` runs mypy for Python 3.9 and 3.12. Release-note environments drive Towncrier and `news` commits NEWS changes.

## State and Persistence
Tox manages virtualenvs under its work directory. Coverage commands produce coverage files/XML. `news` mutates `NEWS.rst` and creates a git commit when run. `tarballs` builds source and wheel artifacts. Integration tests may create temporary runtime data.

## Dependencies and Integration Points
Integrates with Twisted Trial, coverage, ruff, mypy, Sphinx, Towncrier, PyInstaller, Chutney for Tor integration, Tahoe CLI, setup.py packaging, and GitHub Actions via `tox-gh-actions`.

## Risks and Test Signals
`news` runs `git commit`, which is intentionally side-effectful. `integration` depends on a pinned Git URL and platform selectors. Type checks pin Twisted and mypy versions, so dependency drift can alter results. Test signals are passing tox envs, especially `codechecks`, `typechecks`, `py*-coverage`, and `integration`; packaging confidence comes from `pyinstaller` and `tarballs`.
