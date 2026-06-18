# File Research: sources/os/linux/linux/fs/smb/server/proc.c

This file implements ksmbd procfs monitoring support and global per-CPU counters.

Procfs layout:
- Creates `/proc/fs/ksmbd`.
- Creates a `sessions` directory under it.
- Creates a `server` proc entry via `ksmbd_proc_create()`.

Counters:
- Defines global `struct ksmbd_counters ksmbd_counters`.
- Initializes and destroys all `percpu_counter` entries.
- `ksmbd_proc_reset()` sets counters to zero.
- Server stats include sessions, tree connects, read bytes, written bytes, and per-SMB2-command request counts.

Server stats display:
- Prints server string, NetBIOS name, workgroup, min/max protocol strings, server flags, fake filesystem capabilities, and aggregate counters.
- Maps SMB2 command indexes to stable names from negotiate through oplock break.

Lifecycle:
- `ksmbd_proc_init()` creates procfs directories, initializes counters, creates the server stats entry, and resets counters.
- Any init failure calls `ksmbd_proc_cleanup()` for partial cleanup.
- `ksmbd_proc_cleanup()` removes the proc tree and destroys counters.

Role in this group:
- Called from `server.c` module init and cleanup paths.
- Helper declarations live in `misc.h`.
- Session proc entries are declared through `user_session.h` and implemented by session management code.
