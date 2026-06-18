# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/stat.c

Implements `debugreiserfs -t` statistics over selected blocks.

Behavior:
- Initializes an obstack and binary tree of unique item headers.
- Scans the input bitmap.
- Keeps only blocks that look like leaves or broken-header leaves with item arrays.
- Counts total items, unique items, leaves, skippable blocks, and item types.
- Clears bitmap bits for non-leaf blocks and leaf blocks containing no unique items.
- If an input bitmap filename was supplied, saves the updated bitmap back to that file.

Uniqueness comparison uses key ordering plus item length and entry count.

Purpose: identify duplicate/redundant leaf content and optionally produce a reduced bitmap for later pack/scan operations.

Notable quirks:
- Comments say statistics do not fully work.
- A second pass is unreachable because the function returns before it.
