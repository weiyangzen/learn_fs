# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/checks.am

Automake test build fragment for mkfs/grow/jadd Check tests.

Behavior:
- Defines `TESTS = check_grow check_jadd check_mkfs`.
- Builds check programs from production target source lists plus each `check_*.c`.
- Adds `-DUNITTESTS` to suppress production `main()` blocks.
- Adds Check framework CFLAGS/LIBS and suppresses unused-function warnings.

Risk notes:
- Since tests compile production source directly, static helper coverage can be added later.
- Current test source files are stubs.
