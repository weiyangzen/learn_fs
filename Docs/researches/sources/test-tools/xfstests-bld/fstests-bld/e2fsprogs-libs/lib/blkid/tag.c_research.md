# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/tag.c

## Purpose
`tag.c` owns libblkid tag allocation, mutation, iteration, parsing, and indexed lookup by tag type/value.

## Important APIs, Types, and Functions
Important functions include `blkid_find_tag_dev()`, `blkid_dev_has_tag()`, `blkid_set_tag()`, `blkid_parse_tag_string()`, `blkid_tag_iterate_begin()`, `blkid_tag_next()`, `blkid_tag_iterate_end()`, and `blkid_find_dev_with_tag()`. Internal helpers allocate tags and cache-level tag heads.

## Control Flow
`blkid_set_tag()` duplicates the value, updates or deletes an existing device tag, creates cache tag-head entries as needed, links tags into both the device list and per-name cache list, and maintains direct `bid_type`, `bid_label`, and `bid_uuid` pointers. `blkid_find_dev_with_tag()` reads the cache, searches the tag-name index by priority, verifies stale hits, probes new devices, and finally probes all devices if necessary.

## State, Persistence, Dependencies, Risks, and Test Signals
State spans each device tag list, cache tag-head index, direct common tag pointers, iterator magic, priority fields, and cache changed flags. Dependencies include list macros, cache/probe APIs, `access()`, and `blkid_verify()`. Risks include pointer lifetime coupling between `bit_val` and `bid_*`, iterator invalidation during mutation, duplicated tag-head management, and expensive fallback probing. Test signals include exact tag replacement/deletion, UUID/LABEL lookup by priority, iterator traversal, and cache-change detection.
