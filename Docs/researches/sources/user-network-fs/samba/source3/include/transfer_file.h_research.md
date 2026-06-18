# sources/user-network-fs/samba/source3/include/transfer_file.h

## Purpose
`transfer_file.h` declares utility functions for copying bytes from one file-like object to another, either through caller-provided pread/pwrite callbacks or plain file descriptors.

## Important APIs, Types, and Functions
- `transfer_file_internal(void *in_file, void *out_file, size_t n, ssize_t (*pread_fn)(...), ssize_t (*pwrite_fn)(...))`: generic transfer loop over abstract file handles.
- `transfer_file(int infd, int outfd, off_t n)`: descriptor-based wrapper that transfers up to `n` bytes.

## Control Flow and State
The implementation is expected to repeatedly read from the input and write to the output until the requested byte count, EOF, or error. The internal function's callbacks allow VFS-like or test-specific file abstractions.

## Persistence Behavior
The output file descriptor/object is modified with copied bytes. No long-term state is kept by the helper itself.

## Dependencies and Integration Points
It integrates with source3 file-copy paths, potential VFS copy fallbacks, and tests that need to inject read/write functions. It uses POSIX-like `ssize_t` and `off_t` semantics.

## Risks
- Partial reads/writes, short writes, EINTR/EAGAIN, and large `off_t` values must be handled in the implementation.
- The generic callback interface cannot enforce whether input/output offsets are advanced by callback behavior or by the helper.
- Descriptor wrapper must not assume sparse/offloaded copy semantics.

## Test Signals
Tests should cover zero-length transfer, EOF before requested count, partial read/write callbacks, write errors, large transfers, and descriptor-to-descriptor copies.
