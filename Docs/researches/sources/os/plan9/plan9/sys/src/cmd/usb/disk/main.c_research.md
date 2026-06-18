# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/disk/main.c

Read fully: 72 lines, 1196 bytes. SHA-256 prefix: `7f418d51b444ca81`.

This is the entry point for the USB disk server command. It parses debug, device-number, mountpoint, and srv options; initializes `usbfs`; then starts all matching USB mass-storage devices with `diskmain()`.

Supported class/subclass/protocol matches include ATAPI bulk, SFF-8070 bulk, and SCSI transparent bulk storage. Default mountpoint is `/n/disk`.

Integration: delegates all per-device behavior to `disk.c`; uses shared USB discovery helpers `startdevs()`, `matchdevcsp()`, and `usbdirfs`.

Risk notes: command-line arguments are forwarded into a bounded 80-byte `args` buffer. Excessive option text could be truncated by `seprint()` rather than rejected.
