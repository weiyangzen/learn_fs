# File Research: sources/windows/reactos/drivers/filesystems/npfs/prefxsup.c

## Purpose
Provides prefix-table lookup helpers for resolving absolute and root-relative pipe names.

## Main Responsibilities
- `NpFindPrefix`:
  - Calls `RtlFindUnicodePrefix` on `NpVcb->PrefixTable`.
  - Returns the containing FCB/DCB by using the shared `PrefixTableEntry` field layout.
  - Computes the unmatched suffix in `Prefix`, skipping a leading separator.
- `NpFindRelativePrefix`:
  - Builds a temporary absolute name by prepending `\` to a relative name.
  - Calls `NpFindPrefix`.
  - Rewrites `Prefix->Buffer` back to point into the original relative name.
  - Returns the found FCB.

## Important Interactions
- Used by create/open paths and wait handling.
- Depends on `NP_FCB` and `NP_DCB` sharing the same `PrefixTableEntry` offset, asserted in `npfs.h`.

## Risks / Review Notes
- `NpFindPrefix` bugchecks if no prefix entry is found, so callers expect at least the root DCB prefix to always exist.
- `NpFindRelativePrefix` allocates a temporary name and relies on careful pointer recalculation after freeing it.
