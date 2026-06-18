# File Research: sources/os/linux/linux/fs/smb/server/mgmt/user_config.c

This file manages KSMBD user objects returned by userspace IPC.

Main behavior:
- `ksmbd_login_user()` sends a login request to userspace, checks `KSMBD_USER_FLAG_OK`, optionally fetches extended group data, and allocates a user.
- `ksmbd_alloc_user()` copies account name, flags, uid/gid, NT hash/passkey, and optional supplementary groups.
- `ksmbd_free_user()` sends logout IPC and frees groups, name, passkey, and object.
- `ksmbd_anonymous_user()` detects empty-name users.
- `ksmbd_compare_user()` compares name and passkey for session reuse checks.

The file keeps user credentials as kernel-owned copies while relying on userspace for account database lookup.
