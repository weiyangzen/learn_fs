# File Research: sources/os/linux/linux/mm/kasan/report_tags.c

## Role

Shared tag-based KASAN report classification for software and hardware tag modes. It searches the tag-mode allocation/free stack ring to infer bug type and recover allocation/free tracks.

## Key Functions

- `get_common_bug_type()` classifies wrapped/negative-size accesses as out-of-bounds and otherwise returns `invalid-access`.
- `kasan_complete_mode_report_info()` scans `stack_ring` backwards under its write lock.
- It matches entries by untagged object address, pointer tag, and cache object size.
- First matching free entry tends to classify the bug as `slab-use-after-free`.
- First matching allocation entry tends to classify the bug as `slab-out-of-bounds`.
- It copies matching alloc/free `kasan_track` records into the report and falls back to common classification if no entry is found.

## Dependencies

Uses the global `kasan_stack_ring` from `tags.c`, atomic ring position, tag helpers, slab cache metadata, and KASAN report structures.

## Research Notes

Tag-based bug classification is best-effort because ring entries can be overwritten and a later allocation with the same tag can reuse the address. The report is probabilistic but still gives useful recent allocation/free context.
