# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio.h

Defines the public ZIO interface, block checksumming structures, checksum/compression/encryption constants, I/O flags, bookmarks, child types, transform stack, `zio_t`, allocation helpers, I/O constructors, execution APIs, fault injection, checksum ereports, and bookmark comparison helpers.

Key elements:
- `zio_eck_t` is the embedded checksum trailer.
- `zio_gbh_phys_t` defines self-checksumming gang block headers.
- `enum zio_checksum` lists supported checksum algorithms and pseudo-values.
- Encryption data lengths are defined for objset MAC, data IV, salt, and MAC.
- `enum zio_flag` controls aggregation, repair, scrub/resilver, physical I/O, failure behavior, caching, retry, queueing, raw compression/encryption, gang/DDT child state, nopwrite, reexecution, and delegation.
- `zbookmark_phys_t` identifies blocks by objset/object/level/blkid and has special root/ZIL/dnode conventions.
- `zio_prop_t` carries checksum, compression, object type, level, copies, dedup/nopwrite, small block, encryption metadata, byteorder, salt/IV/MAC.
- `zio_t` stores core I/O identity, callback state, data ABDs, vdev state, timing, pipeline state, errors, child/parent counts, gang state, synchronization, FMA checksum report, and taskq dispatch state.

Main dependencies and interactions:
- Includes priority, context, SPA, TXG, AVL, ZFS public definitions, and `zio_impl.h`.
- Used across DMU, vdev, ZIL, spa sync, scrubs, resilver, fault injection, and ereporting.

Implementation notes:
- `ECKSUM` and `EFRAGS` reuse otherwise-unused errno values.
- Child flag macros define which flags propagate to DDT, gang, and vdev child I/Os.
- The `zio_t` structure is central pipeline state; lock and child counters are correctness-critical.
