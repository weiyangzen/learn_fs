<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/Makefile -->
# sources/test-tools/xfstests/tests/xfs/Makefile

Purpose: build and install rules for the xfstests `xfs` test directory.

Important APIs, types, and functions: includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`, sets `XFS_DIR`, `TARGET_DIR`, and `DIRT = group.list`, and defines `install`.

Control flow: the default target builds generated dirt such as `group.list`. `install` creates the target xfs test directory and installs executable `$(TESTS)`, `group.list`, and output files with the expected modes.

State and persistence behavior: generated state is limited to `group.list`; installed files are copied into `$(PKG_LIB_DIR)/$(TESTS_DIR)/xfs`.

Dependencies and integration points: integrates with the top-level xfstests make infrastructure and packaging install paths.

Risks and test signals: incorrect modes would break test execution or output comparison. The empty `install-dev install-lib` targets intentionally do nothing.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/xfs/Makefile -->
