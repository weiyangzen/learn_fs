# sources/test-tools/lcov/tests/common.mak

Purpose: shared Makefile fragment for all LCOV tests. It discovers repository paths, exports common tool commands, prepares generated `.info` fixtures, dispatches tests through `runtests.py`, and defines common cleanup.

Important variables/targets: computes `TOPDIR`, `TESTDIR`, `ROOT_DIR`, `BINDIR`, `SCRIPTDIR`, `TESTBINDIR`, `IS_GIT`, `IS_P4`, `ANNOTATE_SCRIPT`, `VERSION_SCRIPT`, coverage wrappers, fixture paths, `LCOV`, `GENHTML`, `OPTS`, and `TESTS`. Targets include `check`, `checkdeps`, `prepare`, generated `$(INFOFILES) $(COUNTFILES)`, `clean`, `clean_echo`, and `clean_subdirs`.

Control flow and state: included Makefiles define `TESTS`, then `check` calls `$(TOPDIR)/bin/runtests.py $(TESTS) $(OPTS)`. On first include only (`_ONCE` guard), `check` depends on dependency checks and fixture generation through `mkinfo`. Tool paths and language are exported for child tests. Cleanup delegates to `cleantests.py`.

Dependencies and integration: central integration point for lcov binaries, support scripts, Python/Perl coverage, generated fixture data, and subdirectory Makefiles.

Risks and test signals: git/P4 detection controls annotation/version callback selection, so environment changes affect test behavior. The `_ONCE` guard prevents repeated preparation in recursive includes. Makefile variable overrides like `TESTS` are filtered from sub-makes. Main signal is every `make check` under this tree.
