# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.h

Read status: complete.

## Purpose
Defines ksmbd user account state and accessors.

## Main Contents
- `struct ksmbd_user` with flags, uid, gid, name, passkey, and supplementary groups.
- Helpers for guest flag, arbitrary user flags, passkey/name/uid/gid access.
- APIs for login, allocation from IPC responses, free, anonymous check, and comparison.

## Dependencies And Role
Shared by auth, session, and tree-connect code.

## Risks
The empty `set_user_guest()` helper is intentionally inert in this version; callers should rely on flags from userspace rather than expecting it to mutate state.
