# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse_if.h

## Purpose
Defines the public/internal callback interface between perfuse core code and a FUSE frame transport implementation.

## Main Responsibilities
- Defines paths and protocol constants such as `_PATH_FUSE`, `_PATH_PERFUSED`, `PERFUSE_MOUNT_MAGIC`, unknown inode/nodeid sentinels.
- Defines diagnostic flags and logging/error macros.
- Defines `perfuse_msg_t`, exchange reply modes, callback function pointer types, and `struct perfuse_callbacks`.
- Defines mount request metadata in `struct perfuse_mount_out` and `struct perfuse_mount_info`.
- Duplicates minimal FUSE input/output header definitions to avoid exposing full private `fuse.h`.
- Declares public perfuse lifecycle and helper APIs.

## Key Implementation Notes
- Diagnostics can print foreground, syslog, FUSE/PUFFS frames, file handles, readdir, sync, resize, trace, and queue events.
- `DERR`/`DERRX` abort in foreground mode but use `err`/`errx` otherwise.

## Dependencies
- PUFFS types and minimal FUSE header layout.
