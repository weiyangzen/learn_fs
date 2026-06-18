<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prottab.h -->
# sources/security-integrity/audit-userspace/auparse/prottab.h

## Purpose
Maps memory protection bits to names for `mmap` and `mprotect` interpretation.

## Important APIs, types, and functions
The `_S` table includes read, write, exec, sem, growsdown, and growsup protection bits.

## Control flow
Generated data is scanned by `interpret.c:print_prot`, with special handling for `PROT_NONE` when low permission bits are zero.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Tracks asm-generic mman constants and feeds syscall argument interpretation for memory events.

## Risks and test signals
Risks are arch-specific flags and missing protection bits. Tests should cover `PROT_NONE`, combined protections, mmap-specific `PROT_SEM`, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/prottab.h -->
