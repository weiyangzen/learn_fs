# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sendfile.h

## Role

Defines the `sendfile()` and `sendfilev()` user ABI, vector layouts, large-file remapping, and syscall subcodes.

## Key Interfaces

- `sendfilevec_t` describes one source: file descriptor, flags, offset, and length.
- `SFV_NOWAIT` requests nonblocking behavior.
- Large-file `sendfilevec64_t` is exposed under `_LARGEFILE64_SOURCE`.
- Kernel syscall32 structures handle ILP32 and ILP32-largefile copyin; the 64-bit variant uses packing on amd64 where needed.
- `SFV_FD_SELF` permits self-process data as a source.
- Subcodes: `SENDFILEV` and `SENDFILEV64`.
- Userland declares `sendfilev()`, `sendfile()`, and transitional `sendfilev64()`/`sendfile64()`.

## Compatibility Notes

The header uses `redefine_extname` or macros to map 32-bit `_FILE_OFFSET_BITS=64` applications to the 64-bit interfaces, while LP64 maps largefile aliases back to native names.

## Risk Notes

Vector layout, packing, and large-file symbol mapping are ABI-critical for 32-bit and 64-bit applications.
