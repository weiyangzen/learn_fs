# File Research: sources/virtualization/libguestfs/daemon/dd.c

Implements dd-style whole-copy and fixed-size copy APIs.

Key points:
- `do_dd` builds `if=` and `of=` arguments for raw devices or sysroot files and invokes `dd bs=1024K`.
- `do_copy_size` copies exactly `ssize` bytes in-process, supporting file/device source and destination.
- File destinations are created/truncated; device destinations are opened writable.
- Reports progress during fixed-size copy.
- Detects short input and read/write/close errors.
