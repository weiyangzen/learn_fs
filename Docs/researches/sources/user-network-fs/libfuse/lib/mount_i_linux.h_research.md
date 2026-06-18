# sources/user-network-fs/libfuse/lib/mount_i_linux.h

## Purpose
Linux-private mount header defining the concrete `struct mount_opts` and Linux-only mount/new-mount helper APIs.

## Important APIs, Types, And Functions
- `struct mount_opts` contains option booleans, mount flags, fsname/subtype strings, and three option buffers for subtype, mtab, helper, and kernel use.
- Declares direct mount preparation, mtab option construction, new mount API entry points, sync-init helper IPC, and fsconfig helper functions.
- Documents the role of `dest_mnt_fd` in `fuse_kern_fsmount` for avoiding mountpoint TOCTOU in helper mode.

## Control Flow
No executable control flow. The documentation here clarifies sequencing: `set_fsconfig_ms_flags` runs before `ms_flags_to_mount_attrs`, and sync-init obtains a fd before sending a proceed signal to complete mounting.

## State And Persistence
No state. It defines ownership and semantic contracts for heap strings and fd-based mount targets.

## Dependencies And Integration Points
Includes Linux mount headers and is shared by `mount.c`, `mount_fsmount.c`, `fusermount.c`, and `mount_service.c`.

## Risks
Header comments describe critical security assumptions; callers that pass `-1` instead of a pinned mount fd remain path-resolution based. Struct layout is internal but must stay consistent across C files compiled into libfuse utilities.

## Test Signals
Compile with and without `HAVE_NEW_MOUNT_API`, validate declarations match definitions, and run sync-init tests confirming the caller cannot proceed until the worker sends the ready signal.
