<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml

Purpose: adds one export to an existing kdevops NFS server, creating requested storage, setting permissions and SELinux context, writing `/etc/exports.d/<name>.exports`, and reloading exports.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.set_fact`, `ansible.builtin.template`; variables/facts `file`, `become_flags`, `become_method`, `changed_when`, `failed_when`, `template_export_options`, `fsid_is_present`; tasks `Add a local logical volume for the new export`, `Add an iSCSI LUN for the new export`, `Add a tmpfs for the new export`, `Ensure {{ export_volname }} has correct permissions`, `Test whether SELinux is enabled`.

Control flow: Includes local, iSCSI, or tmpfs storage tasks based on variables; fixes permissions; detects SELinux; ensures `/etc/exports.d`; adds a generated fsid for tmpfs when absent; optionally appends `pnfs`; templates the export file; runs `exportfs -ra`.

State and persistence behavior: Persists mounted storage, export directories, `/etc/exports.d` files, SELinux contexts, and NFS export table state on `server_host`.

Dependencies and integration points: Used by nfstest and pynfs to create per-test exports. Depends on `server_host`, storage roles, `exports.j2`, `uuidgen`, and nfsd being configured.

Risks: The pNFS branch overwrites `template_export_options` from `export_options` rather than preserving a generated tmpfs fsid. `/etc/exports.d` mode is `644` on a directory, which is unusual. Parallel export edits are partly serialized only in downstream roles.

Test signals: Signals are mounted export path, valid export file, `exportfs -ra` success, unique fsid for tmpfs, and client mount success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml -->
