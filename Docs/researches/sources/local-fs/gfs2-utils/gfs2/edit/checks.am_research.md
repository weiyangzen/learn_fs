# File Research: sources/local-fs/gfs2-utils/gfs2/edit/checks.am

## Purpose
Automake test fragment for `gfs2_edit`.

## Main Elements
- `TESTS = check_edit`.
- Builds `check_edit`.
- Reuses `$(gfs2_edit_SOURCES)` plus `check_edit.c`.
- Adds `-DUNITTESTS`, Check CFLAGS/LIBS, and suppresses unused-function warnings.

## Dependencies And Integration
Included only under `if HAVE_CHECK` from `Makefile.am`.

## Risk Notes
Because the test binary links the editor source set, missing external dependencies still break tests even though the test body is a stub.
