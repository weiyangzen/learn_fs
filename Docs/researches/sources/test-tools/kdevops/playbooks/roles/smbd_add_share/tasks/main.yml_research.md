<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml

Purpose: adds one Samba share backed by LVM or tmpfs storage and reloads the SMB service.

Important APIs/types/functions: modules `community.general.lvol`, `community.general.filesystem`, `ansible.posix.mount`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.blockinfile`, `ansible.builtin.systemd_service`; variables/facts `become_flags`, `become_method`, `vg`, `lv`, `size`, `fstype`, `dev`, `throttle`, `changed_when`, `failed_when`; tasks `Create a new LVM partition`, `Format new volume for {{ share_fstype }}`, `Mount volume under {{ smbd_share_path }}`, `Mount tmpfs under {{ smbd_share_path }}`, `Ensure {{ share_volname }} has correct permissions`.

Control flow: Delegates to the server, creates/formats/mounts an LVM volume or tmpfs, sets permissions, restores SELinux context, inserts a templated share block into `/etc/samba/smb.conf` with `blockinfile`, and reloads `smb.service`.

State and persistence behavior: Persists LV/filesystem/mount or tmpfs, share directory metadata, smb.conf block, SELinux relabeling, and service reload.

Dependencies and integration points: Depends on configured `server_host`, `share_volname`, `share_fstype`, templates, VG `shares`, and a running Samba setup.

Risks: Parallel fstab and smb.conf edits are throttled but still sensitive to inventory concurrency. tmpfs shares are volatile. No validation with `testparm` occurs before reload.

Test signals: Signals are mounted path, smb.conf block, successful reload, `testparm`, and client access to the share.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml -->
