# sources/user-network-fs/nfs-utils/tests/Makefile.am

Purpose: `tests/Makefile.am` wires top-level nfs-utils tests and the `statdb_dump` helper into automake.

Important build APIs and control flow: It builds `statdb_dump` from `statdb_dump.c`, links support NFS, NSM, misc, and optional cap libraries, descends into `nsm_client`, and declares `t0001-statd-basic-mon-unmon.sh` as the test. `EXTRA_DIST` packages `test-lib.sh` and tests.

State, dependencies, and integration: Test binaries depend on built support libraries, generated NSM code, and system capabilities for statd integration.

Risks and test signals: `t0002-nfsconf.sh` and `tests/nfsconf` fixtures are present but not listed in `TESTS` in this snapshot. Tests should run `make check`, ensure linked libraries are current, and confirm distributed test fixtures are complete.
