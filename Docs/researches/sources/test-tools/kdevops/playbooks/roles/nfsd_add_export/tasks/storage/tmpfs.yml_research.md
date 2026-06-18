<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml

Purpose: mounts a tmpfs-backed directory for an NFS export.

Important APIs/types/functions: modules `ansible.posix.mount`; variables/facts `become_flags`, `become_method`, `throttle`, `fstype`; tasks `Mount a tmpfs under {{ nfsd_export_path }}`.

Control flow: Delegates to `server_host` and mounts `tmpfs` at `nfsd_export_path/export_volname`.

State and persistence behavior: Persists an fstab/system mount entry for tmpfs and runtime memory-backed contents.

Dependencies and integration points: Used when `export_fstype == tmpfs`; main export task adds a unique fsid if needed.

Risks: Tmpfs contents are volatile and consume RAM; missing stable fsid can confuse NFS clients across remounts.

Test signals: Signals are mounted tmpfs, export file with fsid, and successful NFS client access.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml -->
