# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/fs.c

Generic 9P server framework for USB driver file trees.

Core elements:
- Defines `Rpc` state containing incoming/outgoing `Fcall`, fid pointer, flush state, and data buffer.
- Manages fid and RPC freelists under `rpclck`.
- Implements 9P operations: version, attach, walk, open, read, write, clunk, stat, flush, and permission-denied stubs.
- Dispatches blocking open/read/write work to a small cached process pool managed by `schedproc`.
- `usbdirread` serializes generated directory entries.
- `usbreadbuf` serves static buffers with offset/count semantics.
- `usbfsinit` creates a pipe-backed 9P server, optionally posts it in `#s`, and optionally mounts it.

Important behavior:
- Only one user is allowed after first attach unless username matches.
- Flush marks an RPC as flushed but does not abort underlying I/O.
- On 9P read failure it calls `fsops->end` or closes the underlying device.

This is the foundation used by `usbdirfs`, Ethernet, serial, and `usbdctl` file trees.
