<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile -->
# sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile

Purpose: Developer convenience Makefile for the vendored `extras` package.

Important APIs/functions: `check` runs `PYTHONPATH=$(PWD) $(PYTHON) -m testtools.run extras.tests.test_suite`; `TAGS` and `tags` generate editor tags over `extras/`; `clean` removes tags and `*.pyc`; `apidocs` runs `pydoctor` with project metadata.

Control flow: Make targets execute shell commands. `SOURCES` is computed by `find extras -name "*.py"`.

State and persistence behavior: `check` only runs tests. Tags and apidocs create generated files/directories; `clean` removes tags and bytecode.

Dependencies and integration points: Depends on `make`, Python, testtools, ctags, and pydoctor. WiredTiger can use it when validating or maintaining the vendored package in isolation.

Risks: `find ... -exec rm '{}' \;` removes all pyc files under `extras`; safe for source tree cleanup but broad. `apidocs` depends on pydoctor not usually present in test environments. `PYTHON` defaults to `python`, which may point to an unexpected interpreter.

Test signals: `make check` is the primary test signal and should run the included `extras.tests.test_suite`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/extras-0.0.3/Makefile -->
