## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFallocate.cc

Purpose: supplies a macOS implementation of `posix_fallocate()`.

Important APIs/types/functions: `int posix_fallocate(int fd, off_t offset, off_t len)` is compiled only under `__APPLE__`. It uses `fcntl(F_PREALLOCATE)` with `fstore_t`, first requesting contiguous allocation and then falling back to non-contiguous allocation, followed by `ftruncate(fd, offset + len)`.

Control flow: detects signed overflow of `offset + len` with `__builtin_saddll_overflow`; on no overflow, tries contiguous preallocation, then all-or-nothing preallocation, then extends/truncates file size. On overflow or failed fcntl/ftruncate, returns a negative system-call-style result.

State and persistence: mutates file allocation and potentially file length for the supplied descriptor. No process-global state.

Dependencies and integration: macOS `fcntl`, `unistd`, and stat/types headers. Paired with `XrdSysFallocate.hh` so XRootD code can call `posix_fallocate` uniformly.

Risks: POSIX `posix_fallocate` normally returns an error number rather than `-1` with `errno`; this implementation returns raw negative syscall status. `ftruncate` may alter size even when the original file was larger/smaller according to platform semantics.

Test signals: macOS sparse file allocation, overflow inputs, fragmented allocation fallback, `ftruncate` failure, and consistency with caller expectations for return convention.
