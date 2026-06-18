# File Research: sources/os/bsd/freebsd-src/sys/sys/devicestat.h

## Purpose
Defines the kernel/user ABI and kernel APIs for block/device I/O statistics exposed through devstat.

## Main Elements
- Constants: `DEVSTAT_NAME_LEN`, `DEVSTAT_DEVICE_NAME`, `DEVSTAT_VERSION`.
- Enums describe supported statistic features, transaction direction, tag type, priority/list ordering, and device type/interface flags.
- `struct devstat` records sequence counters, active/completed operations, busy time, creation time, block size, bytes/operations/durations per direction, tag counts, identity, and device metadata.
- Kernel APIs create/remove entries and start/end transactions directly or from `bio`.

## Dependencies And Integration
Includes queue and time headers; kernel side integrates with storage drivers, GEOM, CAM, and bio accounting.

## Risk Notes
`DEVSTAT_VERSION` must change when ABI-relevant layout or enum ordering changes. Sequence counters are used to read coherent snapshots from userland.
