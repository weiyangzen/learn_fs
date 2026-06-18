# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iomdl.c

## Purpose

Implements I/O manager wrappers for MDL allocation, partial MDL construction, and MDL freeing.

## Main APIs

- `IoAllocateMdl`
- `IoBuildPartialMdl`
- `IoFreeMdl`

## Behavior

`IoAllocateMdl` validates nonzero length, rejects allocations with the high bit set, calculates the page span, and either uses a fixed-size MDL lookaside entry for small MDLs up to 23 pages or allocates a variable-size MDL from nonpaged pool. It initializes the MDL with `MmInitializeMdl`, marks fixed-size MDLs with `MDL_ALLOCATED_FIXED_SIZE`, and optionally attaches the MDL to an IRP as primary or secondary buffer.

`IoBuildPartialMdl` derives a target MDL from a source MDL, copies selected source flags, marks the target as `MDL_PARTIAL`, computes `MappedSystemVa`, and copies the relevant PFN array subset.

`IoFreeMdl` prepares the MDL for reuse, then returns fixed-size MDLs to the I/O manager lookaside list or frees pool-backed MDLs with `TAG_MDL`.

## Filesystem Relevance

This file supports direct I/O paths used by filesystem and storage IRPs. In this group, `iofunc.c` calls `IoAllocateMdl` for direct device controls, directory queries, reads, writes, and related user buffer pinning.

## Dependencies and Coupling

Depends on memory manager MDL primitives, I/O manager lookaside list helpers, PFN layout immediately after `MDL`, and pool tag `TAG_MDL`.

## Research Notes

- Small MDLs are optimized through a fixed-size lookaside allocation path.
- Secondary-buffer insertion assumes an existing IRP MDL chain is present before walking `Irp->MdlAddress`.
