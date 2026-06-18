<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml

Source read: complete file, 6 lines, 170 bytes, sha256 `8198ed5bb5f95e6a`. Final split target: `Docs/researches/sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml_research.md`.

Purpose: defaults for mounting an NFS export as the data path.

Important APIs/types/functions: `nfs_mount_options`, `nfs_mounted_on`, `nfs_server_hostname`, and `nfs_server_export`.

Control flow: no tasks; consumed by `create_nfs_mount/tasks/main.yml`.

State and persistence behavior: defaults target `/data` mounted from `kdevops-nfsd:/export`.

Dependencies and integration: supports workflows using shared NFS data storage instead of local disks/tmpfs.

Risks: default hostname assumes a matching inventory/DNS entry. Mount options are plain `defaults`, with no explicit version, retry, or timeout.

Test signals: variable resolution should show the intended server/export before the mount role runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/create_nfs_mount/defaults/main.yml -->
