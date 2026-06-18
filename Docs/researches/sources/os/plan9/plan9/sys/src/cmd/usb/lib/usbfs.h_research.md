# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usbfs.h

Header for the USB 9P file server framework.

Defines:
- Message/buffer sizing constants.
- `Fid` state with fid number, qid, open mode, next pointer, and aux field.
- `Usbfs` operation table for walk, clone, clunk, open, read, write, stat, and end.
- `Dirgen` callback type.
- Utility functions for reading static buffers, adding/removing file systems, directory reads, and starting the USB file server.
- Shared error strings and exported `usbdirfs`.

This is the contract implemented by `fs.c` and `fsdir.c` and consumed by USB drivers.
