<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml

Purpose: defines default NFS server export settings: export root, default filesystem/storage choices, and service behavior knobs used by `nfsd` and `nfsd_add_export`.

Important APIs/types/functions: variables/facts `nfsd_export_label`, `nfsd_export_fs_opts`, `nfsd_lease_time`, `nfsd_export_storage_local`, `nfsd_export_storage_iscsi`, `kdevops_krb5_enable`.

Control flow: Defaults are read by Ansible variable resolution before task execution.

State and persistence behavior: No runtime state; values shape later directory, storage, and export creation.

Dependencies and integration points: Consumed by NFS server setup and test roles such as pynfs/nfstest that request exports.

Risks: Unsafe defaults can expose broad export permissions if templates use them directly; changes affect multiple workflows.

Test signals: Validate by rendering exports with expected path, fs type, storage mode, and options.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml -->
