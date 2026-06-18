# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/checks.am

## Purpose
Automake test fragment for `fsck.gfs2`.

## Main Elements
- `TESTS = check_fsck`.
- Builds `check_fsck`.
- Reuses `$(fsck_gfs2_SOURCES)` plus `check_fsck.c`.
- Adds `-DUNITTESTS`, Check flags, and warning suppressions for unused const variables/functions.

## Dependencies And Integration
Included only when `HAVE_CHECK` is true.

## Risk Notes
The test target links all fsck sources even though the test itself is a stub, so broad build dependencies affect test build success.
