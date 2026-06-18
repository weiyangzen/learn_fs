# File Research: sources/windows/reactos/ntoskrnl/mm/amd64/procsup.c

## Role In Subset

Implements amd64 process address-space creation support for ARM3, specifically architecture-specific setup after generic process directory table pages have been allocated.

## Main Responsibilities

- `MiArchCreateProcessAddressSpace` initializes a new process PML4 and hyperspace paging hierarchy.
- Uses provided `DirectoryTableBase` entries for the top-level table and hyperspace root.
- Allocates/zeroes pages for hyperspace PD and PT, preferring zeroed pages and falling back to any page plus `MiZeroPhysicalPage`.
- Reserves a system PTE to temporarily map and edit the new process page tables.
- Clears user half of the top-level table and copies kernel mappings from the current address space.
- Writes self-map, hyperspace, hyperspace PD/PT, and working-set-list mappings.
- Releases temporary system PTEs before returning.

## Locking And State Assumptions

- PFN lock is used while removing pages from zero/free lists.
- The non-architecture code is assumed to have already allocated the top-level and hyperspace pages.
- TLB invalidation is done with `__invlpg` after remapping the temporary system PTE to point at different paging levels.

## Notable Limitations

- Returns `FALSE` only if temporary system PTE reservation fails; allocated hyperspace pages are not visibly unwound in that failure case.
- Depends on amd64 paging constants and ARM3 templates established in `amd64/init.c`.

## Filesystem-Relevant Notes

Every process address space must contain correct kernel and hyperspace mappings before filesystem-facing syscalls can safely copy buffers, fault pages, or access working-set data for mapped files.
