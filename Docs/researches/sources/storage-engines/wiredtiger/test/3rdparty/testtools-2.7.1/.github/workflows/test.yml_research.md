# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/.github/workflows/test.yml

Purpose: upstream GitHub Actions CI workflow for the vendored `testtools` 2.7.1 package.

Important APIs, types, and functions: workflow `Test` runs on `push` and `pull_request`. Matrix covers CPython 3.7 through 3.12 and PyPy 3.9/3.10 on Ubuntu 20.04. Steps check out full history, set up Python, cache pip, install build/test/docs dependencies, run tests, and build docs. A dependent `success` job prints a success marker.

Control flow: each matrix job installs `pip`, `setuptools`, `wheel`, `setuptools_scm`, `sphinx`, and `.[test,twisted]`; then runs `python -W once -m testtools.run testtools.tests.test_suite`; then runs `make clean-sphinx docs`.

State and persistence: CI state is limited to runner workspace and pip cache. No project runtime state is persisted except GitHub cache entries.

Dependencies and integration points: integrates with GitHub Actions, `actions/checkout`, `actions/setup-python`, `actions/cache`, package extras, `testtools.run`, and Sphinx docs make targets.

Risks and test signals: pinned action versions may become outdated; Ubuntu 20.04 and old Python versions can age out of hosted runner support. Test signals are matrix test success and documentation build success.
