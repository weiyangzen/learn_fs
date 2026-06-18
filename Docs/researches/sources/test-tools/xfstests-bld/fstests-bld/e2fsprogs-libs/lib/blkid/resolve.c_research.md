# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/resolve.c

## Purpose
`resolve.c` implements libblkid convenience lookup APIs that map devices to tag values and tag expressions to device names.

## Important APIs, Types, and Functions
The public functions are `blkid_get_tag_value()` and `blkid_get_devname()`. The test main exercises both modes.

## Control Flow
When no cache is supplied, each function creates a temporary default cache and releases it before returning. `blkid_get_tag_value()` finds a device with `blkid_get_dev()` and duplicates the requested tag value. `blkid_get_devname()` accepts either `(token, value)` or a single `NAME=value` token, treats a token without `=` as a literal device name, then calls `blkid_find_dev_with_tag()`.

## State, Persistence, Dependencies, Risks, and Test Signals
State changes occur through cache reads and any probing triggered by `blkid_find_dev_with_tag()`. Returned strings are heap-owned by the caller. Dependencies include `blkidP.h`, `tag.c`, cache creation, and device lookup code. Risks include NULL handling, ambiguous unescaped `NAME=value` input, and implicit disk probing when cache misses. Test signals are correct UUID/LABEL resolution, literal path passthrough, temporary cache cleanup, and the `TEST_PROGRAM` cases.
