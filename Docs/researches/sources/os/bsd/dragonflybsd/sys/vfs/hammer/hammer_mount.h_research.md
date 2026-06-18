# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_mount.h

## Purpose
Defines the userland-to-kernel HAMMER mount argument structure and public mount flags.

## Key Elements
- `struct hammer_mount_info` carries volume device names, volume count, HAMMER-specific flags, mirror master ID, and `asof` mount TID.
- `master_id` supports no-mirror mode via `-1` or mirror master IDs `0-15`.
- Defines mount flags for no-history, explicit master ID, no mirror, and dirty undo state.
- `HMNT_USERFLAGS` limits user-settable mount flags to no-history, master ID, and no-mirror.

## Dependencies
Includes `<sys/types.h>` and `<sys/mount.h>` with include guards so it can be shared by mount tooling and kernel code.

## Behavior/Risks
This is a small ABI header. Reserved fields preserve structure layout compatibility, including space formerly used for export arguments.
