<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/Makefile -->
# sources/test-tools/xfstests/tests/btrfs/Makefile

Final split target: `Docs/researches/sources/test-tools/xfstests/tests/btrfs/Makefile_research.md`.

Source read: 24 lines, SHA256 prefix `bf36f162ed492618`.

Purpose: package-install rules for the xfstests `btrfs` test directory. It builds the local `group.list` metadata and installs runnable tests plus expected output files into the package test tree.

Important APIs/types/functions: the file includes `include/builddefs`, `include/buildgrouplist`, and `$(BUILDRULES)`. Important variables are `TOPDIR`, `TARGET_DIR`, and `DIRT`. The exported targets are `default`, `install`, `install-dev`, and `install-lib`.

Control flow: `default` depends on `$(DIRT)`, which is the generated `group.list`. The `install` target creates `$(TARGET_DIR)`, installs `$(TESTS)` executable, installs `group.list` read-only, and installs `$(OUTFILES)` as read-only golden-output files. `install-dev` and `install-lib` are intentionally empty.

State and persistence behavior: persists directory contents under `$(PKG_LIB_DIR)/$(TESTS_DIR)/...` during package installation and leaves `group.list` as a build artifact. It does not run tests or touch scratch devices.

Dependencies and integration: integrated with the xfstests build system through `builddefs`, `buildgrouplist`, and common build rules. It depends on the harness variables that enumerate tests and `.out` files.

Risks: install permissions are fixed at 0755 for tests and 0644 for metadata/output; missing generated group lists or stale `$(TESTS)` expansion would omit cases from packaged runs.

Test signals: `make -C tests/btrfs install DESTDIR=...` should create the expected tree with executable test scripts, `group.list`, and output files.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests/tests/btrfs/Makefile -->
