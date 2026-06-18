# File Research: sources/os/bsd/netbsd-src/lib/libutil/passwd.c

## Purpose
Password database editing, locking, copying, and password configuration lookup helpers.

## Key Details
- Maintains optional `pw_prefix` for alternate root/database paths.
- `pw_lock` creates `_PATH_MASTERPASSWD_LOCK` with exclusive create and retry loop.
- `pw_mkdb` runs `pwd_mkdb` via `vfork/execv`.
- `pw_abort` removes the lock file.
- `pw_init` adjusts resource limits and ignores common signals for editing.
- `pw_edit` runs `$EDITOR` or `vi` through the shell and handles stopped editor processes.
- `pw_copyx` copies master password entries, replacing or appending a target user entry, while checking old-entry consistency if provided.
- `pw_getconf` parses `/etc/passwd.conf` sections and options.
- `pw_getpwconf` tries user-specific, group-specific, then default password config.

## Dependencies and Role
- Security-sensitive account database tooling.
- Uses filesystem locks and temporary master password files.
