# File Research: sources/virtualization/libguestfs/daemon/fallocate.c

Implements file allocation APIs.

Key points:
- `do_fallocate` rejects negative 32-bit length and delegates to `do_fallocate64`.
- `do_fallocate64` opens/truncates a sysroot file for writing.
- Uses `posix_fallocate` when available.
- Fallback writes zero-filled buffers until requested length is reached.
- Reports open, allocation/write, and close errors.
