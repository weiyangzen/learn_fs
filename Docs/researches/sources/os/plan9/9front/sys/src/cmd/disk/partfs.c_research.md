# File Research: sources/os/plan9/9front/sys/src/cmd/disk/partfs.c

9P file server that exposes byte ranges of an underlying disk image/file as devsd-style partitions.

Key behavior:
- Serves a root containing an sd-like directory, `ctl`, and partition files.
- Initializes a default `data` partition over the entire underlying file.
- `ctl` reports inquiry, geometry, and partitions; writes support `part`, `delpart`, `inquiry`, and `geometry`, passing unknown commands through to an underlying ctl file when serving a device directory.
- Partition reads/writes translate request offsets through partition sector offsets and clamp to partition length.
- Qid versions invalidate stale fids after partition recreation.
- Supports read-only open of the underlying image with `-r`, custom sd name, mountpoint, and service name.

Notable dependencies:
- Plan 9 thread/9p libraries.
- Underlying file or `<dir>/data` plus optional `<dir>/ctl`.

Research notes:
- No explicit locking protects global partition state; typical 9P service serialization may be relied on.
- `evommem` is a wrapper around `memmove` with reversed argument naming and is unused in the read file.
