# sources/test-tools/xfstests/tests/nfs/Makefile


Purpose: Build/install glue for the xfstests nfs test directory.


Important APIs, helpers, and commands: Includes `builddefs`, `buildgrouplist`, and `$(BUILDRULES)`; sets `NFS_DIR`, `TARGET_DIR`, and `DIRT=group.list`.



Control flow, state, dependencies, risks, and test signals: Default builds group.list; install creates the NFS package test directory, installs test scripts executable, and installs group.list/outfiles read-only. State is generated group.list and installed artifacts. Dependencies are top-level make variables and xfstests build rules. Risks are missing TESTS/OUTFILES or wrong target dir. Signals are make/install success. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
