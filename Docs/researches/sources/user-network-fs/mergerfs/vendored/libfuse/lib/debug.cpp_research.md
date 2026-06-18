<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp

Purpose: This file implements line-oriented FUSE protocol tracing. It decodes request and reply payloads into readable key/value logs and emits init summaries to syslog.

Important APIs and flow: `fuse_debug_set_output` switches `fuse_cfg` logging to stderr or an append-mode line-buffered file with safe `FILE*` ownership. Helpers quote strings/data, format open/FUSE/write/fopen/init flags, print xattr values as text or hex, and timestamp records with `CLOCK_MONOTONIC`. `fuse_debug_in_header` locks the output `FILE`, prints common request header fields, switches on opcode, and delegates to opcode-specific payload printers. Output functions print structured replies for open, init, entry, attr, entry+open, readlink, write, statfs, xattr, locks, bmap, statx, data, ioctl, poll, and generic error headers.

State and integration: persistent state is the global `fuse_cfg` log sink and path. The implementation depends on `fuse_kernel.h` ABI structs, fmt, libc `FILE*`, syslog wrappers, and errno/string helpers. It is called from request dispatch and reply functions when debug logging is enabled.

Risks and test signals: debug decoding must stay synchronized with opcodes and struct layouts. Some newer open flags are not included in `_fuse_fopen_flag_to_str`, so logs may omit flags such as passthrough or noflush. String parsing assumes kernel payloads are NUL-terminated where the protocol promises names. Tests should feed synthetic request buffers for each opcode, check concurrency does not interleave lines, verify file-output switching/closing, and compare init flag names for high `flags2` bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp -->
