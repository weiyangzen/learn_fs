<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/Makefile -->
# sources/test-tools/xfstests/tests/perf/Makefile

## Purpose
Build/install metadata for this xfstests directory. It includes xfstests shared build definitions, derives the package target directory, generates `group.list`, installs executable tests and expected-output files, and leaves development/library install targets empty.

## Important APIs, Types, And Functions
Make variables include `TOPDIR`, directory-specific `*_DIR`, `TARGET_DIR`, and `DIRT`; targets include `default`, `install`, `install-dev`, and `install-lib`; included rule files are `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`.

## Control Flow
The makefile imports xfstests shared build rules, declares `group.list` as generated dirt, and installs tests, `group.list`, and expected output files into the package tests directory. Development and library install targets are intentionally empty.

## State And Persistence
State is build/install metadata only. Generated state is `group.list`; install state is the packaged test directory populated by `$(INSTALL)`.

## Dependencies And Integration Points
Depends on xfstests top-level make fragments and the `TESTS`/`OUTFILES` lists supplied by the build system.

## Risks And Test Signals
Risks are packaging omissions: wrong target directory names, missing group-list generation, or mode mismatches on installed executable tests. A successful `make install` and populated target directory are the main test signals.

<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/perf/Makefile -->
