# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/fs/zfs.h

This header defines ZFS Fault Management Architecture event class names and payload member names. It contains constants only; there are no structures or functions.

Primary class:
- `ZFS_ERROR_CLASS` is `"fs.zfs"`.

Ereport subclasses:
- General ZFS error reports include checksum, authentication, I/O, data, delay, zpool, I/O failure, probe failure, log replay, and config-cache write failures.
- Vdev-specific reports include unknown device, open failure, corrupt data, no replicas, bad GUID sum, too small, bad label, and bad ashift.

Payload names:
- Pool metadata: pool name/id, failmode, GUID, and pool context.
- Vdev metadata: GUID, type, path, devid, FRU, state, ashift, and delay counters.
- Parent vdev metadata: parent GUID, type, path, and devid.
- ZIO location/error metadata: objset, object, level, block id, errno, offset, and size.
- Checksum diagnostics: expected/actual checksum, algorithm, byteswap flag, bad offset range data, set/clear histograms, and bit counters.

Other constants:
- Failmode values are `"wait"`, `"continue"`, and `"panic"`.
- Resource event names include removed, autoreplace, and statechange.

Dependencies and relationships:
- Used by ZFS kernel/userland FMA producers and consumers to agree on nvlist field names and event class suffixes.
- Complements `sys/fm/protocol.h`, which defines generic FMA event and FMRI field names.
