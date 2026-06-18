## sources/test-tools/kdevops/workflows/gitr/nfs/Kconfig

Purpose: Configures gitr execution over NFS, including server source, export path, mount options, and dedicated NFS feature sections.

Important APIs/types/functions: Symbols include `GITR_USE_KDEVOPS_NFSD`, `GITR_NFS_SERVER_HOSTNAME`, `GITR_NFS_SERVER_EXPORT`, `GITR_NFS_MOUNT_OPTS`, and section flags for pNFS, RDMA, NFSv4.2/v4.1/v4.0/v3.

Control flow: Server settings are selected first; section selectors are exposed only in dedicated gitr workflow mode.

State and persistence: Kconfig values become `GITR_ARGS` and `GITR_ENABLED_TEST_GROUPS`.

Dependencies and integration points: `GITR_USE_KDEVOPS_NFSD` selects `KDEVOPS_SETUP_NFSD`. The Makefile maps this into NFS server/export vars for the gitr playbook.

Risks and test signals: External NFS server exports are not deeply validated by Kconfig. Test by checking generated mount command and running a simple Git test on the mounted path.
