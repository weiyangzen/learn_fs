# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disk.c

DragonFly BSD managed disk layer. It wraps raw disk driver devices with cooked disk/slice/partition devices, probes partition metadata, routes I/O through slices, and coordinates disk lifecycle through a serialized message thread.

Key responsibilities:
- Creates raw and managed disk `cdev_t` devices, devfs aliases, udev metadata, dsched integration, and iocom state.
- Updates disk media info and triggers asynchronous or synchronous probing through `disk_msg_core`.
- Probes MBR/GPT slices, creates slice devices, probes BSD disklabel32/64 partitions, creates partition devices, and maintains `serno`, label, UUID, slice, and partition aliases.
- Serializes probe, reprobe, unprobe, and destroy operations through lwkt disk messages and `ds_token`.
- Implements disk open/close, ioctl routing, strategy I/O, psize, crash dump configuration, disk enumeration, and disk locate helpers.
- Provides `bioqdisksort()` read-before-write ordering with write trickle/burst controls and media-size bounds checking.

Important behavior:
- `disk_setdiskinfo()` copies media geometry/serial data, derives missing media size/block count, updates scheduler state, then probes the disk.
- `disk_probe()` replaces the slice table, calls `mbrinit()`, creates slice devices, and probes BSD labels only for compatibility/BSD-like slices.
- `diskstrategy()` uses `dscheck()` to translate slice-relative offsets to raw-device offsets before dispatching to the raw strategy routine.
- Opens are serialized with `DISKFLAG_LOCK`; the raw device is opened on the first slice/partition open and closed after the last close.
- Reprobe preserves existing devfs nodes by marking valid devices with `SI_REPROBE_TEST` and destroying stale related nodes afterward.

Dependencies:
- Depends on disk slice and disklabel ops, MBR/GPT probing, devfs, raw driver `dev_ops`, buffer/BIO APIs, lwkt ports/tokens, kernel dump, dsched, udev, and UUID helpers.

Notable risks:
- Disk probing is asynchronous by default, so consumers must tolerate device-node appearance after `disk_setdiskinfo()`.
- Correctness depends on `dscheck()`, disklabel ops, and devfs reprobe flags staying in sync across slice/partition changes.
- Raw/cooked device layering has special cases for device-mapper and `D_NOEMERGPGR`.
- `bounds_check_with_mediasize()` mixes `DEV_BSIZE` offset conversion with caller-provided sector size/media units, matching legacy assumptions.
