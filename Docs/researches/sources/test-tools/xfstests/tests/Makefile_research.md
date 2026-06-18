## sources/test-tools/xfstests/tests/Makefile

Purpose: this makefile coordinates building and installing test subdirectories under `tests/`.

Important variables and targets: `TOPDIR = ..` and `include $(TOPDIR)/include/builddefs` pull in project build definitions. `TESTS_SUBDIRS` discovers lowercase child directories with `$(wildcard $(CURDIR)/[[:lower:]]*/)` and normalizes/sorts them. `SUBDIRS` is the relative lowercase directory list. The default target builds all `$(SUBDIRS)`. `install` depends on every `%-install` target derived from `TESTS_SUBDIRS` and creates `$(PKG_LIB_DIR)/$(TESTS_DIR)`. `install-dev` and `install-lib` intentionally do nothing. `%-install` recurses into each test subdir with `$(MAKE) $(MAKEOPTS) -C $* install`.

Control flow: `default` delegates to directory targets supplied by included build rules. `install` recurses into absolute-ish discovered subdirectories and then ensures the package test directory exists.

State and persistence: build/install state is external to the file and controlled by the included build system. Installation creates directories and files under package paths configured by `builddefs`.

Dependencies and integration: it depends on `include/builddefs`, `$(BUILDRULES)`, make recursion support in each lowercase subdirectory, and standard install tooling.

Risks: only lowercase-named subdirectories are discovered, so mixed-case test directories would be ignored. `TESTS_SUBDIRS` includes `$(CURDIR)` paths while `SUBDIRS` is relative, so included rules must tolerate that split. Recursive make failures propagate through the pattern target.

Test signals: `make -C tests` should recurse through every lowercase test directory. `make -C tests install` should install each subdirectory and create `$(PKG_LIB_DIR)/$(TESTS_DIR)` with mode 755.
