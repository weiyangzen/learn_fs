# File Research: sources/os/plan9/plan9/sys/src/9/port/devaoe.c

This file implements Plan 9’s ATA-over-Ethernet storage initiator as a namespace device.

Key responsibilities:
- Exposes an AoE device tree under device character `æ`, including top-level `aoe`, `ctl`, `log`, per-unit directories, `data`, `config`, `ident`, and `devlink` files.
- Binds Ethernet netlinks, opens AoE EtherType conversations, reads local Ethernet addresses, and spawns per-netlink reader kernel processes.
- Sends AoE config discovery packets, tracks discovered shelves/slots as `Aoedev` units, and maintains per-device links to network interfaces and target Ethernet addresses.
- Implements ATA read/write request scheduling with `Srb` request blocks and `Frame` transmit slots.
- Supports retransmission, round-trip tracking, adaptive max outstanding requests, jumbo-frame fallback, and device-down behavior.
- Parses ATA identify data, stores serial/firmware/model fields, updates device size, flags LBA/power/smart/nop capabilities, and changes qid versions on media changes.
- Reads and writes AoE config strings.
- Provides control commands for bind/unbind, discover, rediscover, debug, remove, identify, failio, jumbo, nofail, mtu/max block count, and setsize.
- Maintains an event log readable from `log`.

Important implementation details:
- Data I/O requires sector-aligned offset and length.
- `rw` splits large requests into bounded SRB chunks and uses copying for user buffers but can reference kernel buffers directly.
- `aoesweepproc` periodically rediscovers devices and resends timed-out frames.
- `netunbind` disables links, waits for reader exit, reschedules packets, compacts devlink arrays, and removes orphan devices.
- `eventlogread` avoids copying to pageable memory while holding the event lock.

Filesystem/storage relevance:
- This is a full block-storage device driver surfaced through the Plan 9 file namespace.
- The `data` file is the block device surface used by higher-level partition/filesystem tooling.
