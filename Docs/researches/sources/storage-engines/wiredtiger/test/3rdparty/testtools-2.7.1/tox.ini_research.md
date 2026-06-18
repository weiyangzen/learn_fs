<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini

Purpose: Vendored `testtools` tox matrix for running its upstream test suite.

Important APIs/types/functions: Defines environments `py36` through `py312` plus `pypy3`; installs editable package with `sphinx`, `setuptools>=61`, `setuptools-scm`, and extras `test` and `twisted`; command is `python -W once -m testtools.run testtools.tests.test_suite`.

Control flow: Tox creates each interpreter environment and runs the single testtools suite command.

State and persistence behavior: Tox creates local virtualenv/build state outside source logic.

Dependencies and integration points: Relevant only when validating the vendored third-party package; not part of WiredTiger CMake tests.

Risks and test signals: Interpreter availability and old Python support are host-sensitive. The test signal is a full tox run or targeted current-interpreter run of `testtools.tests.test_suite`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/tox.ini -->
