# File Research: sources/os/linux/linux/block/blk-ia-ranges.c

## Summary
Implements block-device independent access range registration, validation, replacement, and sysfs exposure. These ranges describe disk LBA regions that can be accessed independently, such as concurrent positioning ranges.

## Main Responsibilities
- Allocate `struct blk_independent_access_ranges` arrays for a disk.
- Validate that ranges are non-empty, contiguous, non-overlapping, sorted by LBA, and exactly cover disk capacity.
- Register `/sys/block/<disk>/queue/independent_access_ranges/<n>/` entries.
- Expose each range’s `sector` and `nr_sectors`.
- Replace or clear a disk’s current range set during setup or revalidation.

## Key APIs
- `disk_alloc_independent_access_ranges()`.
- `disk_set_independent_access_ranges()`.
- `disk_register_independent_access_ranges()`.
- `disk_unregister_independent_access_ranges()`.

## Important Behavior
`disk_check_ia_ranges()` sorts the caller-provided range array in-place by repeatedly finding the range that starts at the next expected sector. It rejects holes, overlaps, zero range count, and a final sector count that does not match `get_capacity(disk)`.

`disk_set_independent_access_ranges()` holds `q->sysfs_lock`, frees invalid or unchanged new ranges, unregisters the old range set, installs the new one, and registers it immediately if the queue is already registered.

Sysfs lifetime is parent-owned: individual range kobjects have a no-op release because the whole flexible array is freed from the parent `blk_independent_access_ranges` kobject release after all children have been deleted.

## State and Synchronization
All public mutation paths use `q->sysfs_lock`. `disk->ia_ranges` is the single owning pointer until sysfs registration transfers final free responsibility to kobject release.

## Risks
The range array is modified during validation, so callers must not depend on original order after `disk_set_independent_access_ranges()`. Lifetime depends on deleting every child kobject before parent release; skipping unregister would leave sysfs references to memory owned by the range set.
