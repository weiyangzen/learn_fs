<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml

Purpose: creates and mounts a local LVM-backed filesystem for a new NFS export.

Important APIs/types/functions: modules `community.general.lvol`, `community.general.filesystem`, `ansible.posix.mount`; variables/facts `become_flags`, `become_method`, `vg`, `lv`, `size`, `fstype`, `dev`, `throttle`; tasks `Create a new LVM partition`, `Format new volume for {{ export_fstype }}`, `Mount volume under {{ nfsd_export_path }}`.

Control flow: Delegates to `server_host`, creates an LVM logical volume in VG `exports`, formats it with `export_fstype`, and mounts it under `nfsd_export_path/export_volname` with fstab persistence.

State and persistence behavior: Persists an LV, filesystem, mount entry, and mounted directory on the server.

Dependencies and integration points: Included by `nfsd_add_export/tasks/main.yml` when local storage is selected.

Risks: Volume creation and fstab edits are stateful and can fail if the VG lacks space or parallel runs collide.

Test signals: Signals are present LV, successful filesystem creation, mounted path, and idempotent rerun.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml -->
