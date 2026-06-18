# File Research: sources/local-fs/gfs2-utils/gfs2/tune/checks.am

Automake test wiring for `tunegfs2`.

Defines:
- `TESTS = check_tune`
- `check_PROGRAMS = $(TESTS)`
- `check_tune_SOURCES = $(tunegfs2_SOURCES) check_tune.c`
- Adds `-DUNITTESTS` and `-Wno-unused-function`
- Links with tune dependencies plus Check libraries.

Research notes:
- `UNITTESTS` excludes the real `main` from `gfs2/tune/main.c`.
