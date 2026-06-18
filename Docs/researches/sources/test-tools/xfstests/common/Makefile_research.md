# sources/test-tools/xfstests/common/Makefile

Purpose: build/install rules for xfstests common helper files.

Important flow: include top-level `include/builddefs` and `$(BUILDRULES)`, set `COMMON_DIR=common`, and define `install` to create `$(PKG_LIB_DIR)/common` and install all files with mode 644. `install-dev` and `install-lib` are empty.

State and dependencies: installation copies common helper scripts into package library directory. Depends on xfstests build system variables and `$(INSTALL)`.

Integration points: makes common shell libraries available to installed tests.

Risks and test signals: installs every file in `common` as non-executable 0644, appropriate for sourced helper files but wrong if an executable lands there. Build tests should verify package contents and modes.
