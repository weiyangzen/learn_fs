<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml

Purpose: sets default ownership, group, and permissions for newly added NFS export directories.

Important APIs/types/functions: variables/facts `export_user`, `export_group`, `export_mode`, `export_pnfs`, `nfsd_export_storage_local`, `nfsd_export_storage_iscsi`.

Control flow: Defaults feed the `file` task after storage and mount setup.

State and persistence behavior: No direct state; values affect directory metadata on server hosts.

Dependencies and integration points: Used by `nfsd_add_export` calls from pynfs/nfstest and other workflows.

Risks: Broad modes or root ownership changes affect client write behavior and test assumptions.

Test signals: Validate by checking created export directory owner/group/mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml -->
