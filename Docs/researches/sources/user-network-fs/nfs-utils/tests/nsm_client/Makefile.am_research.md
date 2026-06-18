# sources/user-network-fs/nfs-utils/tests/nsm_client/Makefile.am

Purpose: `tests/nsm_client/Makefile.am` builds the synthetic NSM client and lockd simulator used by statd tests.

Important build APIs and control flow: It generates `nlm_sm_inter` client, service, XDR, and header files from `nlm_sm_inter.x` using in-tree or system rpcgen, builds `nsm_client` from generated files plus `nsm_client.c`, and links support NFS, NSM, libcap, and tirpc.

State, dependencies, and integration: Generated files are build artifacts listed in `BUILT_SOURCES` and `CLEANFILES`. The binary is used by shell tests to issue SM_MON/UNMON/NOTIFY and emulate NLM callbacks.

Risks and test signals: rpcgen path selection and generated header freshness are common failure points. Tests should cover clean tree builds, dist builds, and execution of generated client/server RPC stubs.
