# File Research: sources/windows/reactos/ntoskrnl/mm/rmap.c

## Purpose

`rmap.c` implements reverse mappings from physical pages back to process virtual addresses or section segment page-table associations. It supports page-out decisions, insertion/deletion of reverse-map entries, segment association lookup, and section-association removal.

## Main Contents

- Initializes an NPaged lookaside list for `MM_RMAP_ENTRY` objects in `MmInitializeRmapList`.
- Pages out a physical page with `MmPageOutPhysicalAddress`.
- Adds mappings with `MmInsertRmap`.
- Removes mappings with `MmDeleteRmap`.
- Looks up section segment reverse maps with `MmGetSegmentRmap`.
- Deletes section associations with `MmDeleteSectionAssociation`.

## Behavior And Data Flow

`MmInsertRmap` allocates a reverse-map entry, normalizes non-segment addresses to page boundaries, verifies that the process PTE maps the expected PFN, and inserts the entry into the PFN's sorted rmap list under the PFN lock. Non-segment entries also increase the process working-set size and update the peak.

`MmPageOutPhysicalAddress` first finds a non-segment rmap entry for the page. It protects the target process from rundown, references it, locks the address space, attaches if needed, verifies the mapping still points to the target PFN, and handles section-view page-out. Private dirty pages may receive a newly allocated swap entry, be temporarily replaced with `MM_WAIT_ENTRY`, written to the paging file, and then replaced with a pagefile mapping. If swap allocation or writeback fails, the mapping is restored and marked dirty. Shared section-backed pages are released through section-segment accounting. If no process rmap can release the page, the code checks segment association and dirty segment state.

## Concurrency And Invariants

- PFN rmap list head access is guarded by the PFN lock through `MmGetRmapListHeadPage` and `MmSetRmapListHeadPage`.
- Process lifetime is protected with rundown protection plus object referencing during page-out.
- Address-space locks and process attach are used before process PTE inspection or mutation.
- Duplicate reverse-map entries for the same process/address are fatal.
- `MmGetSegmentRmap` requires the PFN lock and specifically checks for segment deletion state.

## Notable Details

- Segment reverse maps encode a page-table slice pointer in the `Process` field and a low-byte page index in a special masked address value.
- `MmPageOutPhysicalAddress` has several restore-on-failure paths to avoid losing dirty private pages when swap allocation or writeback fails.
- The `NEWCC` cache-area branch references `Type` rather than `MemoryArea->Type`, which appears suspicious in the shown code and should be checked if that conditional path is enabled.
- Working-set size is adjusted only for process virtual-address rmaps, not segment association entries.
