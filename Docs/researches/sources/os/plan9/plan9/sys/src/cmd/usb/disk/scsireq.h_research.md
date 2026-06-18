# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/scsireq.h

Read fully: 176 lines, 5291 bytes. SHA-256 prefix: `34c6adb150e1b6df`.

This header defines SCSI request structures, flags, status codes, sense bits, device types, endian helpers, and function prototypes used by USB disk and other SCSI consumers.

`ScsiReq` stores unit path, LUN, logical block size, block offset, raw fd, USB LUN pointer, command/data buffers, returned status, sense data, inquiry data, and flags. `ScsiPtr` describes a command or data transfer buffer and direction.

Integration: included by `disk.c`, `main.c`, and `scsireq.c`. It declares `umsrequest()` as the USB transport hook and many SCSI/MMC/changer prototypes, including functions not implemented in this local `scsireq.c` subset.

Risk notes: `Maxiosize` is tied to Plan 9 devmnt message sizing. The header contains a non-ASCII exponent comment in `Max24off`; generated or ASCII-only tooling should avoid altering semantics.
