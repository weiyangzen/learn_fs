# File Research: sources/os/plan9/9front/sys/src/9/port/sdram.c

Plan 9 `SDifc` RAM disk driver backed by reserved physical memory exposed through a segment.

Key responsibilities:
- Supports up to four `ramdiskN` devices configured through kernel configuration strings.
- Parses size values with `K`, `M`, `G`, and `T` suffixes, with optional `+`/`-` adjustment syntax.
- Allocates RAM disk pages either from the end of existing memory banks or by excluding a fixed physical range from `conf.mem`.
- Creates a physical cached, no-exec segment for each online RAM disk.
- Exposes RAM disks as `sd` units with SCSI-style inquiry data and geometry reporting.
- Implements raw block I/O through `segio()`, including sector-size and page-offset handling.
- Implements `rio` by delegating fake SCSI handling and fake SCSI read/write parsing to shared helpers.

Dependencies:
- Uses kernel memory-bank configuration, `Segment`, `Segio`, `Physseg`, and the port `sd` layer.
- Calls `newseg()` and `segio()` from the segment subsystem.

Notable behavior:
- Default sector size is 512 bytes.
- `ramdiskX=size`, `ramdiskX=size ss`, and `ramdiskX=base size ss` are supported.
- The reported alignment includes page size and sector offset derived from the original base address.
