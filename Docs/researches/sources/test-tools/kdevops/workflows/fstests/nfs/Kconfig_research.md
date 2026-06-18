## sources/test-tools/kdevops/workflows/fstests/nfs/Kconfig

Purpose: Configures NFS fstests, including use of a kdevops knfsd server, manual coverage across NFS protocol/transport features, and Kerberos auth flavor selection.

Important APIs/types/functions: Symbols include `FSTESTS_USE_KDEVOPS_NFSD`, `FSTESTS_NFS_SERVER_HOST`, `FSTESTS_NFS_MANUAL_COVERAGE`, section selectors for pNFS, RDMA, TLS, nfsd, v4.2/v4.1/v4.0/v3, and `FSTESTS_NFS_AUTH_FLAVOR`.

Control flow: Server mode is selected first. Manual coverage exposes detailed sections; automatic mode enables a default section and leaves v3 off. A separate auth choice is shown only when Kerberos setup is enabled.

State and persistence: Kconfig choices persist in `.config`; auth flavor and selected sections are later rendered into `FSTESTS_ARGS`.

Dependencies and integration points: `FSTESTS_USE_KDEVOPS_NFSD` selects `KDEVOPS_SETUP_NFSD`; TLS depends on `KDEVOPS_SETUP_KTLS`; auth choice depends on `KDEVOPS_SETUP_KRB5`. The Makefile passes these into Ansible roles.

Risks and test signals: Network feature sections depend on external infrastructure such as RDMA, kTLS, Kerberos, and knfsd exports. Test signals include inventory with an `nfsd` host, rendered `fstests_nfs_auth_flavor`, and successful NFS mounts for each selected section.
