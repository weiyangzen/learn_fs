# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/disk.c

Read fully: 805 lines, 16221 bytes. SHA-256 prefix: `f75832a7be89a77b`.

This file implements the per-device USB mass-storage file server and bulk-only SCSI transport. It exposes each logical unit as an `sdU<dev>.<lun>` USB filesystem with `ctl`, `raw`, and `data` files.

Initialization finds bulk IN/OUT endpoints, resets the device, gets max LUN, runs SCSI inquiry/start/capacity for each usable disk-like LUN, handles large capacity via READ CAPACITY(16), and registers a `Usbfs` per LUN. `ctl` reports inquiry and geometry in sd-compatible text form.

`umsrequest()` wraps SCSI command/data/status in USB bulk-only `Cbw` and `Csw` structures, transfers data, handles stalls, validates signatures/tags/status, maps failures to SCSI status, and performs reset/unstall recovery. Too many errors detach the device and remove LUN filesystems.

`dread()`/`dwrite()` implement directory reads, raw command phase handling, and block data I/O. `setup()` maps byte offsets/counts into block-aligned transfers, using an intermediate buffer for unaligned reads/writes and enforcing `Maxiosize`.

Integration: `main.c` discovers matching USB storage devices and calls `diskmain()`. `scsireq.c` calls `umsrequest()` for `Fusb` requests.

Risk notes: only SCSI command-set mass storage is supported, not ATA. The raw interface has a strict command/data/status phase machine. Unaligned writes perform read-modify-write and reset cached capacity after errors because media may have changed.
