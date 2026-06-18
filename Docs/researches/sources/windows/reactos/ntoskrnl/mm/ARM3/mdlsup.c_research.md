# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/mdlsup.c

## Purpose

`mdlsup.c` implements ARM3 Memory Descriptor List support: creating and sizing MDLs, building MDLs for nonpaged pool, allocating/freeing pages for MDLs, probing and locking pages, mapping locked pages into kernel or user address space, unmapping those mappings, reserved mapping support, and process-specific probe-and-lock helpers.

## Main State

- `MmTrackPtes` and `MmTrackLockedPages` are global tracking toggles.
- `MmSystemLockPagesCount` tracks system locked pages.
- `MiCacheOverride[MiNotMapped + 1]` counts cache-attribute override cases during user mappings.

## User-Space Locked Page Mapping

`MiMapLockedPagesInUserSpace` maps an MDL into the current process:

- computes page count from MDL virtual address and byte count
- translates requested cache type using `MiPlatformCacheAttributes`
- charges nonpaged pool quota for a long VAD
- allocates and initializes an `MMVAD_LONG` as `VadDevicePhysicalMemory`
- either finds an empty user range or validates a caller-specified page-aligned base
- locks the process address space and working set
- inserts the VAD into the process VAD tree
- flushes caches for noncached mappings
- creates valid user PTEs for each MDL PFN
- creates missing PDEs as needed
- increments page-table references and PDE page share counts
- honors existing PFN cache attributes when PFN database entries exist, recording overrides in `MiCacheOverride`
- returns the mapped address plus original MDL byte offset

On failure it unlocks the address space, frees the VAD, returns quota, and raises the failing status.

`MiUnmapLockedPagesInUserSpace`:

- locates the VAD for the base address
- verifies it is `VadDevicePhysicalMemory`
- removes it from the VAD tree
- returns VAD quota
- clears each valid PTE
- decrements page table share/reference counts
- deletes empty PDEs
- flushes the process TLB
- unlocks working set and address space
- frees the VAD

## MDL Creation and Sizing

- `MmCreateMdl` allocates an MDL from nonpaged pool with `TAG_MDL` if the caller did not provide one, then initializes it.
- `MmSizeOfMdl` returns `sizeof(MDL)` plus one `PFN_NUMBER` per spanned page.

## Nonpaged Pool MDLs

`MmBuildMdlForNonPagedPool`:

- asserts the MDL is not already locked, mapped, partial, or marked nonpaged
- clears `Mdl->Process`
- sets `MappedSystemVa` to the original nonpaged VA
- walks the backing PTEs and stores PFNs into the MDL PFN array
- sets `MDL_SOURCE_IS_NONPAGED_POOL`
- sets `MDL_IO_SPACE` if the final PFN has no PFN database entry

## Allocating and Freeing MDL Pages

- `MmAllocatePagesForMdl` delegates to `MiAllocatePagesForMdl` with `MiNotMapped`.
- `MmAllocatePagesForMdlEx` validates flags, translates cache type, and delegates to `MiAllocatePagesForMdl`.
- `MmFreePagesFromMdl` frees pages allocated for an MDL:
  - requires IRQL <= `APC_LEVEL`
  - rejects `MDL_IO_SPACE`
  - validates page-aligned `StartVa`
  - walks the MDL PFN array
  - verifies each PFN is deleted, share count is one, and `PteFrame == 0x1FFEDCB`
  - clears allocation markers and moves pages toward standby/decrement-reference handling
  - replaces freed MDL entries with `LIST_HEAD`
  - clears `MDL_PAGES_LOCKED`

Invalid PFN state during free causes a `MEMORY_MANAGEMENT` bugcheck.

## Kernel Mapping of Locked Pages

`MmMapLockedPagesSpecifyCache` handles kernel mappings when `AccessMode == KernelMode`:

- validates MDL flags and page count
- translates cache attributes, including I/O-space mappings
- reserves system PTEs
- returns `NULL` or bugchecks with `NO_MORE_SYSTEM_PTES` depending on `MDL_MAPPING_CAN_FAIL` and `BugCheckOnFailure`
- writes valid kernel PTEs for each MDL PFN
- sets `MappedSystemVa` and `MDL_MAPPED_TO_SYSTEM_VA`
- sets `MDL_PARTIAL_HAS_BEEN_MAPPED` for partial MDLs
- returns the byte-offset-adjusted system mapping

For user mappings it delegates to `MiMapLockedPagesInUserSpace`.

`MmMapLockedPages` is the compatibility wrapper using `MmCached`, `BugCheckOnFailure = TRUE`, and `HighPagePriority`.

## Unmapping Locked Pages

`MmUnmapLockedPages`:

- if `BaseAddress` is above user space, treats it as a kernel/system PTE mapping:
  - computes page count
  - validates `MDL_MAPPED_TO_SYSTEM_VA`
  - handles `MDL_FREE_EXTRA_PTES` by extending the range backward according to extra count stored after the MDL PFN array
  - clears mapping flags
  - releases the system PTE range
- otherwise delegates to `MiUnmapLockedPagesInUserSpace`

Kernel unmapping relies on `MiReleaseSystemPtes` to return the PTE range.

## Probing and Locking Pages

`MmProbeAndLockPages`:

- validates MDL shape and flags
- validates user-mode address range against `MM_USER_PROBE_ADDRESS`
- probes each page under SEH by reading it and optionally probing for write
- records write intent in `MDL_WRITE_OPERATION`
- sets `MDL_PAGES_LOCKED`
- uses the PFN lock for kernel addresses and the process working-set lock for user addresses
- faults in missing pages through `MmAccessFault`
- handles user copy-on-write faults for write/modify operations
- rejects non-writable pages for write operations when COW cannot be resolved
- references each valid PFN and bumps lock count through `MiReferenceProbedPageAndBumpLockCount`
- marks `MDL_IO_SPACE` when a PFN has no PFN database entry
- records PFNs in the MDL array
- updates `Process->NumberOfLockedPages` for user buffers

On failure after pages are marked locked, it releases the relevant lock, calls `MmUnlockPages`, and raises the status.

## Unlocking Pages

`MmUnlockPages`:

- requires `MDL_PAGES_LOCKED`
- automatically unmaps any system VA mapping first
- handles MDLs marked `MDL_IO_SPACE` by dereferencing only PFNs that exist in the PFN database, then clears `MDL_IO_SPACE` and `MDL_PAGES_LOCKED`
- returns locked-page accounting to the process when present
- converts the MDL PFN array into PFN-entry pointers for non-I/O pages
- takes the PFN lock and calls `MiDereferencePfnAndDropLockCount` for each locked page
- clears `MDL_PAGES_LOCKED`

It explicitly asserts that AWE MDLs are unsupported.

## Reserved Mapping Support

`MmMapLockedPagesWithReservedMapping` maps an MDL into a pre-reserved system PTE range:

- expects two helper PTEs immediately before `MappingAddress`
- validates the stored pool tag in helper PTE 1
- validates helper PTE 0 contains a range size of at least three PTEs
- fails if the reserved range is smaller than the MDL page count
- writes PTEs for MDL PFNs
- sets `MappedSystemVa` and mapping flags
- returns `MappingAddress + Mdl->ByteOffset`

`MmUnmapReservedMapping`:

- validates the same helper PTE tag and size metadata
- verifies a resident system PTE mapping
- handles `MDL_FREE_EXTRA_PTES`
- zeros the PTEs
- flushes the TLB
- clears mapping flags

Misuse causes `SYSTEM_PTE_MISUSE` bugchecks with reason codes for wrong owner, invalid address, or empty mapping.

## Process-Specific Probe and Lock

`MmProbeAndLockProcessPages` attaches to the target process when needed, calls `MmProbeAndLockPages`, and detaches in a `finally` block so exceptions do not leave the caller attached.

## Unimplemented APIs

The file contains stubs for:

- `MmAdvanceMdl`
- `MmPrefetchPages`
- `MmProtectMdlSystemAddress`
- `MmProbeAndLockSelectedPages`
- `MmMapMemoryDumpMdl`

## Notable Details

- Cache attributes are carefully translated and sometimes overridden by existing PFN cache attributes for user mappings.
- Several paths rely on SEH and raise status codes rather than returning them, matching kernel MDL API conventions.
- The code has explicit unsupported areas for large pages, AWE, selected pages, memory dump MDLs, and some protection/prefetch APIs.
- User mappings allocate VAD metadata from nonpaged pool and charge process nonpaged-pool quota for it.
- Kernel mappings use system PTEs; user mappings insert VADs and manipulate process page tables directly.
