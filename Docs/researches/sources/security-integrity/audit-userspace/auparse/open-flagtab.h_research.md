<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/open-flagtab.h -->
# sources/security-integrity/audit-userspace/auparse/open-flagtab.h

## Purpose
Maps file open flag bits to names for `open`, `openat`, `openat2`, and `mq_open` argument interpretation.

## Important APIs, types, and functions
The `_S` table includes write/read-write, create/exclusive/truncate/append, nonblocking/sync/direct/directory/nofollow/noatime/cloexec/path/tmpfile bits. `O_RDONLY` is handled specially in code because it is zero.

## Control flow
Generated table data is scanned by `interpret.c:print_open_flags`, which adds `O_RDONLY` when the access mode is zero and joins set bits.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks asm-generic fcntl flags and feeds syscall argument interpretation plus normalization of file-open operations.

## Risks and test signals
Risks are architecture-specific flag differences and zero-valued flag handling. Tests should cover read-only, combined create/truncate/cloexec, tmpfile/path flags, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/open-flagtab.h -->
