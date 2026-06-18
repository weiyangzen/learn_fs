# File Research: sources/os/plan9/9front/sys/src/cmd/vmx/ide.c

This file implements an emulated legacy IDE/ATA PIO disk controller.

Key behavior:
- Models up to four IDE devices with ATA status/error/control/taskfile registers and per-drive asynchronous I/O state.
- Supports reset, IRQ signaling on IRQ14/15, CHS and LBA sector addressing, address incrementing, PIO read/write buffering, identify-device data, read verify, diagnostics, set translation mode, and selected set-feature commands.
- Uses a background `ideioproc` per disk to read from the backing file and to record writes in an in-memory sector overlay.
- `ideio` handles primary/secondary command/data/control port reads and writes, including 16/32-bit data port transfers.
- `mkideblk` opens a disk image, computes geometry, updates CMOS/int13 metadata, initializes the drive, and starts the I/O process.

Integration and risks:
- Writes are not persisted to the backing file; they are stored in an in-memory sector list.
- Identify-device construction uses fixed strings/fields and has a couple of suspicious `PUT16(d, ...)`/`PUT32(d, ...)` writes where `p` appears intended.
