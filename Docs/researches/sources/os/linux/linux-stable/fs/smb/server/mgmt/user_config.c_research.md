# File Research: sources/os/linux/linux-stable/fs/smb/server/mgmt/user_config.c

Read status: complete.

## Purpose
Fetches, allocates, compares, and frees ksmbd user account configuration.

## Main Responsibilities
- Request login data from userspace IPC and optional supplementary group extension data.
- Allocate `ksmbd_user` with account name, flags, uid/gid, password hash, and supplementary groups.
- Notify userspace on logout during user free.
- Detect anonymous users by empty account name.
- Compare users by name and passkey.

## Dependencies And Role
Used by authentication/session setup and session destruction.

## Risks
Passkey allocation/copy depends on userspace-provided hash size. `ksmbd_compare_user()` assumes comparable passkey sizes are checked by callers where needed.
