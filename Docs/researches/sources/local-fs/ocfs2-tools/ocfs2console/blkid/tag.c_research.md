# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/tag.c

Implements blkid tag lifecycle, tag assignment, tag parsing, tag iteration, and tag-based device lookup.

Key functions:
- `blkid_new_tag`
  - Allocates and initializes a tag object.
- `blkid_free_tag`
  - Removes tag from both linked lists and frees name/value.
- `blkid_find_tag_dev(dev, type)`
  - Finds a tag on one device by name.
- `blkid_find_head_cache(cache, type)`
  - Finds per-tag-name head in cache.
- `blkid_set_tag(dev, name, value, vlength)`
  - Adds, updates, or deletes a tag.
  - Creates per-name cache head if needed.
  - Updates shortcuts:
    - `bid_type`
    - `bid_label`
    - `bid_uuid`
  - Marks cache changed.
- `blkid_parse_tag_string(token, ret_type, ret_val)`
  - Parses `NAME=value`, with optional quote stripping.
- Tag iterator:
  - `blkid_tag_iterate_begin`
  - `blkid_tag_next`
  - `blkid_tag_iterate_end`
- `blkid_find_dev_with_tag(cache, type, value)`
  - Searches tag-name list for exact value.
  - Chooses highest-priority device.
  - Verifies unverified cached matches.
  - Triggers `blkid_probe_all` if cache has not yet been probed.

Notable details:
- Device priority lets EVMS/LVM/MD aliases win over lower-priority duplicates.
- Tag heads are represented as tag objects without device values.
- Deleting a tag also clears shortcut pointers by assigning `NULL`.
