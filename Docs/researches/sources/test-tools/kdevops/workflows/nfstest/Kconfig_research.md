## sources/test-tools/kdevops/workflows/nfstest/Kconfig

Purpose: Configures the nfstest workflow: NFS server source, mount point, nfstest repository/ref, and selected nfstest groups.

Important APIs/types/functions: Symbols include `NFSTEST_USE_KDEVOPS_NFSD`, `NFSTEST_NFS_SERVER_HOST`, `NFSTEST_MNT`, `HAVE_MIRROR_NFSTEST`, `NFSTEST_REPO_CUSTOM`, `NFSTEST_REPO_URL`, `NFSTEST_REPO`, `NFSTEST_REPO_COMMIT`, and group selectors `NFSTEST_TEST_GROUP_*`.

Control flow: Server and repo settings are always available when workflow is enabled; group selectors are exposed in dedicated workflow mode. Default group is interop.

State and persistence: Kconfig persists values in `.config`; Makefile emits nfstest args and group list.

Dependencies and integration points: Selecting kdevops server pulls in `KDEVOPS_SETUP_NFSD`. Repo defaults use default nfstest URL or libvirt mirror.

Risks and test signals: The closing comment says `KDEVOPS_WORKFLOW_ENABLE_GITR`, likely a copy/paste error but not functional. Test by checking generated config, rendered repo/ref, and selected groups.
