# File Research: sources/os/linux/linux-stable/fs/smb/server/glob.h

Read status: complete.

## Purpose
Defines ksmbd-wide debug flags, logging format, Unicode helper macro, and default GFP flags.

## Main Contents
- `ksmbd_debug_types` extern and debug class bits for SMB/auth/VFS/oplock/IPC/connection/RDMA.
- `pr_fmt` override to prefix logs with `ksmbd` and optional submodule name.
- `ksmbd_debug()` conditional logging macro.
- `UNICODE_LEN()` and `KSMBD_DEFAULT_GFP`.

## Dependencies And Role
Included broadly by ksmbd source files for common logging and allocation policy.

## Risks
Debug flag names are token-pasted by `ksmbd_debug(type, ...)`; callers must use valid class names. Allocation policy changes affect many paths.
