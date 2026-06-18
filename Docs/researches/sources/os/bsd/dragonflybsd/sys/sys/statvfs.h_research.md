# File Research: sources/os/bsd/dragonflybsd/sys/sys/statvfs.h

This header defines POSIX `statvfs` filesystem capacity/status ABI plus DragonFly UUID extensions.

Key responsibilities:
- Defines `fsblkcnt_t`, `fsfilcnt_t`, and `uid_t` if needed.
- Under BSD visibility, forward-declares `struct fhandle` and `struct statfs`.
- Defines `struct statvfs`:
  - block size and fragment size
  - total/free/available block counts
  - total/free/available file counts
  - filesystem ID
  - mount flags
  - maximum filename length
  - mount owner UID
  - filesystem type
  - synchronous/asynchronous read/write counters
  - DragonFly filesystem UUID and owner UUID fields
- Defines flags:
  - `ST_RDONLY`
  - `ST_NOSUID`
  - BSD `ST_FSID_UUID`
  - BSD `ST_OWNER_UUID`
- Declares:
  - `fstatvfs()`
  - `statvfs()`
  - BSD `fhstatvfs()`
  - BSD `getvfsstat()`

Important invariants:
- Comments distinguish free blocks from blocks available to unprivileged users.
- DragonFly extensions add full UUID FSID and owner identity beyond the scalar `f_fsid`/`f_owner` fields.
- `ST_FSID_UUID` and `ST_OWNER_UUID` indicate validity of the UUID extension fields.

Research notes:
- This is the filesystem-capacity counterpart to `stat.h`, with DragonFly-specific UUID extensions.
