# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/resolve.c

Public lookup helpers for converting tags to device names and device names to tag values.

Key functions:
- `blkid_get_tag_value(cache, tagname, devname)`
  - Gets a device entry, verifies/probes it through `BLKID_DEV_NORMAL`, and returns an allocated copy of the requested tag value.
  - Creates a temporary cache if caller passes `NULL`.
- `blkid_get_devname(cache, token, value)`
  - If `value` is absent and token lacks `=`, returns a copy of token as a raw device path.
  - If token is `NAME=value`, parses it with `blkid_parse_tag_string`.
  - Finds the best matching cached/probed device by tag via `blkid_find_dev_with_tag`.
  - Returns allocated device path.

Dependencies:
- `blkid_get_cache`, `blkid_put_cache`
- `blkid_get_dev`
- `blkid_find_tag_dev`
- `blkid_find_dev_with_tag`
- `blkid_parse_tag_string`

Notable details:
- Temporary caches are automatically flushed/freed through `blkid_put_cache`.
- Tag lookups can trigger full device probing indirectly through `blkid_find_dev_with_tag`.
