<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seektab.h -->
# sources/security-integrity/audit-userspace/auparse/seektab.h

## Purpose
Maps `lseek` whence values to names.

## Important APIs, types, and functions
The `_S` table covers `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, `SEEK_DATA`, and `SEEK_HOLE`.

## Control flow
Generated `seek_i2s` is used by `interpret.c:print_seek` for `lseek` argument interpretation.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux fs headers and feeds syscall argument `a2` handling for `lseek`.

## Risks and test signals
Risks are new whence constants and masking to `0xFF`. Tests should verify known whence values and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seektab.h -->
