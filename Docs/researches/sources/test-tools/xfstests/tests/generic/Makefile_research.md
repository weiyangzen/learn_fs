# sources/test-tools/xfstests/tests/generic/Makefile


Purpose: Build/install glue for the xfstests generic test directory.


Important APIs, helpers, and commands: Includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`; sets `GENERIC_DIR`, `TARGET_DIR`, and `DIRT=group.list`; defines `install` and empty `install-dev install-lib` targets.



Control flow, state, dependencies, risks, and test signals: The default target builds `group.list`; install creates the package test target directory, installs executable tests as mode 755, installs group.list and golden output files as mode 644. State is build-generated `group.list` and installed files under `$(PKG_LIB_DIR)/$(TESTS_DIR)/generic`. Dependencies are the top-level xfstests build system variables and install tool. Risks are missing generated group.list or incorrect TESTS/OUTFILES expansion. Signals are make/install success. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
