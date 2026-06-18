## sources/test-tools/kdevops/workflows/gitr/nfs/Makefile

Purpose: Emits gitr NFS variables and selected NFS test group labels.

Important APIs/types/functions: Adds `gitr_fstype=nfs`, `gitr_uses_no_devices='True'`, `gitr_nfs_server_host`, `gitr_nfs_server_export`, `gitr_nfs_use_kdevops_nfsd`, `gitr_mount_opts`, and group labels such as `nfs-v42`.

Control flow: Chooses kdevops server host/export or external configured host/export, then appends selected NFS section labels.

State and persistence: No direct state. It feeds Ansible variables and separated test group lists.

Dependencies and integration points: Included by main gitr Makefile for NFS. Integrates with knfsd provisioning and NFS mount roles.

Risks and test signals: NFS mount options are free-form and quoted; bad values fail at runtime. Verify with target mount output and a minimal `git init`/test on the mount.
