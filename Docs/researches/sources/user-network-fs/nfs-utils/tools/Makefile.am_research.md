# sources/user-network-fs/nfs-utils/tools/Makefile.am

Purpose: `tools/Makefile.am` defines the nfs-utils tools subdirectory traversal.

Important build APIs and control flow: It conditionally adds `rpcgen`, `nfsdclddb`, and `nfsrahead` to `OPTDIRS`, always adds `nfsconf`, and sets `SUBDIRS` to locktest, rpcdebug, nlmtest, mountstats, nfs-iostat, rpcctl, nfsdclnts, and optional directories.

State, dependencies, and integration: No runtime state; it coordinates build/install of command-line utilities and test tools.

Risks and test signals: Optional directory ordering matters when generated tools such as rpcgen are needed by later builds. Tests should run configure feature combinations and verify all expected tools are distributed, built, and installed.
