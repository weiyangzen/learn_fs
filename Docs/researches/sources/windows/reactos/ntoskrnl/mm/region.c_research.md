# File Research: sources/windows/reactos/ntoskrnl/mm/region.c

## Purpose

`region.c` manages per-memory-area region lists. A region records a contiguous subrange's type and protection. The file supports initialization, lookup, and alteration of region lists, splitting and merging entries as ranges change.

## Main Contents

- `InsertAfterEntry` inserts a list entry after another list entry.
- `MmSplitRegion` splits one region into before/changed/after portions and invokes an alteration callback for the changed range.
- `MmAlterRegion` changes a range to a new type/protection, frees fully covered regions, splits a trailing partial region, and merges adjacent equal regions.
- `MmInitializeRegion` creates a single initial region covering the full length.
- `MmFindRegion` finds the region containing a given address and optionally returns that region's base address.

## Behavior And Data Flow

`MmAlterRegion` first finds the region that contains the start address. If that region differs from the requested type/protection, `MmSplitRegion` allocates replacement nodes and calls the supplied `AlterFunc` over the affected initial span. The main loop then absorbs complete following regions into the new region, invoking `AlterFunc` for each region whose attributes actually change. A final partial region is shortened if the requested range ends inside it. The result is normalized by merging adjacent regions with matching type and protection.

## Concurrency And Invariants

- The file assumes callers provide any needed synchronization around the region list.
- Region lengths are byte counts and are interpreted relative to a supplied base address.
- Allocation failures during initial splitting return `STATUS_NO_MEMORY`.
- `AlterFunc` is the hook that updates the actual mappings or metadata represented by the logical region change.

## Notable Details

- The merge-with-previous branch adds the old previous region's length to `NewRegion` and removes the previous entry, but does not relink or replace `NewRegion`; callers currently only need success/failure, not the merged node pointer.
- `MmFindRegion` is linear over the region list, which is acceptable for the small per-area lists this legacy subsystem uses.
