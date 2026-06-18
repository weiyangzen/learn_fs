# sources/test-tools/strace/bundled/linux/include/uapi/linux/close_range.h

Purpose: declares the public flag bits for the `close_range(2)` system call.

Important APIs/types/functions: `CLOSE_RANGE_UNSHARE` requests unsharing the file descriptor table before closing or marking descriptors. `CLOSE_RANGE_CLOEXEC` requests setting `FD_CLOEXEC` instead of closing descriptors.

Control flow: the header has no functions. Runtime behavior is in the kernel syscall: callers pass a first descriptor, last descriptor, and ORed flags.

State and persistence behavior: the ABI affects process-local file descriptor table state. `CLOEXEC` persists only until the next exec boundary, while `UNSHARE` changes descriptor-table sharing before the range operation.

Dependencies: no external includes are required beyond the include guard.

Integration points: strace uses these constants to render `close_range` flags. Libraries and tests use them when constructing syscall arguments.

Risks: bit 0 is intentionally absent in this header; decoders must not infer a dense enum. Unknown future bits should remain printable as raw flag values.

Test signals: syscall decode tests should verify no flags, each individual flag, both flags combined, and an unknown bit mixed with known flags.
