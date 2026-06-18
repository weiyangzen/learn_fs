# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/uberblock.h

This public header forward-declares uberblocks and exposes verification/update helpers.

Core API surface:
- `uberblock_t` is an opaque typedef for `struct uberblock`.
- `uberblock_verify()` validates an uberblock.
- `uberblock_update()` updates an uberblock for a root vdev, target TXG, and MMP delay.

Risk-sensitive invariants:
- Actual layout is private to `uberblock_impl.h` but is persistent pool metadata.
- Update must coordinate with root vdev state and MMP heartbeat semantics.
