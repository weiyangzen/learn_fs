# sources/user-network-fs/samba/source3/lib/util_transfer_file.c

## Purpose
This file implements generic fixed-size buffered transfer between random-access file-like objects and a POSIX fd wrapper for normal files.

## Important APIs and Functions
`transfer_file_internal` copies `n` bytes using caller-supplied `pread_fn` and `pwrite_fn` callbacks. `transfer_file` wraps POSIX descriptors with `sys_pread` and `sys_pwrite` through `sys_pread_fn` and `sys_pwrite_fn`.

## Control Flow and State
The transfer allocates a 64 KiB buffer, loops until `total == n` or input EOF, reads at the current offset, then loops on writes until the whole read chunk is written. It returns bytes copied, `0` for zero-length input, or `-1` on read/write allocation errors. It has no durable state.

## Dependencies and Integration Points
It depends on Samba allocation macros, DEBUG, `sys_rw`, and `transfer_file.h`. It is a reusable utility for VFS or file-copy paths that need callback-based copying rather than stream `read`/`write`.

## Risks and Test Signals
On a zero-length write callback, `transfer_file_internal` returns `total` but leaks the allocated buffer because that branch returns before `SAFE_FREE`; that is a concrete cleanup risk. Casting `off_t n` to `size_t` in `transfer_file` can misbehave for negative or too-large values on unusual platforms. Tests should cover short reads, short writes, zero write returns, callback errors, zero-byte transfers, and large transfers crossing the 64 KiB buffer boundary.
