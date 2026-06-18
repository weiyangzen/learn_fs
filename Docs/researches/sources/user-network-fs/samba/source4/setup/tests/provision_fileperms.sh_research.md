# Research: sources/user-network-fs/samba/source4/setup/tests/provision_fileperms.sh

Purpose: validates private-file permissions after provisioning despite selftest's default zero umask.

Control flow: it saves the current umask, sets `0022`, writes a small fake-ACL `smb.conf`, provisions a basic DC, then `check_private_file_perms()` iterates regular files under `private`, uses `stat -c %A`, strips owner bits, and fails if group/other permissions contain write access.

State and dependencies: creates and removes `$PREFIX/basic-dc`; restores the original umask. Depends on GNU-style `stat`, `samba-tool`, and subunit helpers.

Risks and test signals: it skips directories and sockets, so it only covers regular private files. The permission check is direct and provides a strong filesystem-level signal.
