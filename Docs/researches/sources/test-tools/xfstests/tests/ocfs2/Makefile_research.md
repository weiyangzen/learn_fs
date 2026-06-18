# sources/test-tools/xfstests/tests/ocfs2/Makefile


Purpose: Build/install glue for the xfstests ocfs2 test directory.


Important APIs, helpers, and commands: Includes `builddefs`, `buildgrouplist`, and `$(BUILDRULES)`; sets `OCFS2_DIR`, `TARGET_DIR`, and `DIRT=group.list`.



Control flow, state, dependencies, risks, and test signals: Default builds group.list; install creates the OCFS2 package directory, installs executable tests, and installs group.list/outfiles. State is generated group.list and installed artifacts. Dependencies are top-level build variables. Risks are installation path mistakes or missing group data. Signals are successful make/install. Source size is 24 lines, so the logic is small enough to audit as one script but depends heavily on shared xfstests shell libraries for setup, filtering, cleanup, and feature probing.
