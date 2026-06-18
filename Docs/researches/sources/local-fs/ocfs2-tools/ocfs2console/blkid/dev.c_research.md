# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/dev.c

Implements blkid device object lifecycle and public device iteration.

Key functions:
- `blkid_new_dev()`
  - Allocates a zeroed device object.
  - Initializes list links.
- `blkid_free_dev(blkid_dev dev)`
  - Removes the device from the cache device list.
  - Frees all attached tags.
  - Frees device name and object.
- `blkid_dev_devname(blkid_dev dev)`
  - Returns cached device path.
- `blkid_dev_iterate_begin`, `blkid_dev_next`, `blkid_dev_iterate_end`
  - Public iterator API over `cache->bic_devs`.

Dependencies:
- `blkid_free_tag` from `tag.c`
- Local list primitives.

Notable details:
- Iterator hides `list.h` internals from public API users.
- Iterator validity is checked with a magic constant.
