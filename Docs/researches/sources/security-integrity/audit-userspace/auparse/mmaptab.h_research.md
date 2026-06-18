<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mmaptab.h -->
# sources/security-integrity/audit-userspace/auparse/mmaptab.h

## Purpose
Maps `mmap` flag bits to names for syscall argument interpretation.

## Important APIs, types, and functions
The `_S` table includes sharing/fixed/anonymous flags plus grow, denywrite, executable, locked, noreserve, populate, stack, huge page, sync, fixed-noreplace, and uninitialized bits.

## Control flow
Generated `mmap_table` and `mmap_strings` are scanned by `interpret.c:print_mmap`, which joins matching flag names with `|`.

## State and persistence behavior
Static generated table data only.

## Dependencies and integration points
Tracks Linux mman headers. Used for `mmap` `a3` and normalization of memory allocation events.

## Risks and test signals
Risks are missing arch-specific flags and output buffer assumptions. Tests should verify zero handling as `MAP_FILE`, multi-flag joins, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/mmaptab.h -->
