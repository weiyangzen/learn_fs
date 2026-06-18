<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/shm_modetab.h -->
# sources/security-integrity/audit-userspace/auparse/shm_modetab.h

## Purpose
Maps shared-memory mode flag bits to names.

## Important APIs, types, and functions
The `_S` table includes `SHM_DEST`, `SHM_LOCKED`, `SHM_HUGETLB`, and `SHM_NORESERVE`.

## Control flow
Generated data is combined by `interpret.c:print_shmflags` with IPC command flags and permission bits.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux SHM headers and integrates with `ipccmdtab.h` and mode-short rendering.

## Risks and test signals
Risks are missing SHM flags and octal-mask collisions. Tests should validate combined SHM flags and permission formatting.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/shm_modetab.h -->
