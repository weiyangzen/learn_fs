# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/perfuse.c

## Purpose
Provides the public `libperfuse` mount/open shim and initializes a PUFFS usermount backed by FUSE protocol callbacks.

## Main Responsibilities
- Wraps `open("/dev/fuse")` through `perfuse_open()`, connecting to a running `perfused` daemon or spawning `/usr/sbin/perfused`.
- Wraps `mount()` through `perfuse_mount()`, sending a `perfuse_mount_out` frame over the FUSE/perfused communication fd.
- Initializes `struct perfuse_state`, nodeid hash tables, defaults, environment options, and resource limits.
- Registers all `ops.c` filesystem and node operations with PUFFS.
- Creates and caches the root PUFFS node with FUSE root nodeid.
- Provides mainloop, private data accessors, nodeid accessor, forced unmount, unique id allocation, and async filesystem reply handling.

## Key Implementation Notes
- `init_state()` defaults `PS_NO_ACCESS` because some FUSE filesystems perform `access()` checks with incorrect credentials; `PERFUSE_OPTIONS` can enable/disable access and create behavior.
- `perfuse_open()` uses local sockets, preferring `SOCK_SEQPACKET` and falling back to datagrams with a warning.
- `perfuse_init()` sets `MNT_NOSUID|MNT_NODEV` for non-root owners and chooses PUFFS name cache behavior based on TTL support.
- `perfuse_fsreq()` handles fire-and-forget replies, ignoring success and `ENOENT`, warning on connection/transient errors, and warning on unexpected frames.

## Dependencies
- Public API from `perfuse.h` / `perfuse_if.h`.
- Private structures and node helpers from `perfuse_priv.h`.
- PUFFS operation registration macros and mount/mainloop APIs.
