# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/blkidP.h

Internal header for the bundled `libblkid` snapshot used by `ocfs2console` when system blkid is unavailable.

Key contents:
- Defines the internal cache model:
  - `struct blkid_struct_cache`: global cache with `bic_devs`, tag heads, cache file timestamps, flags, filename.
  - `struct blkid_struct_dev`: cached block device with device path, type, priority, `dev_t`, last probe time, flags, label/UUID shortcuts.
  - `struct blkid_struct_tag`: per-device `NAME=value` tag linked both by device and by tag name.
- Defines cache/probe timing:
  - `BLKID_PROBE_MIN` prevents immediate reprobes.
  - `BLKID_PROBE_INTERVAL` controls in-memory revalidation age.
- Defines cache file path `/etc/blkid.tab`, error constants, device priorities for EVMS/LVM/MD, debug masks, and debug dump helpers.
- Declares internal helpers implemented in sibling files:
  - `blkid_read_cache`, `blkid_flush_cache`
  - `blkid_llseek`
  - `blkid_new_dev`, `blkid_free_dev`
  - `blkid_set_tag`, `blkid_find_tag_dev`, `blkid_free_tag`
  - `blkid_strdup`, `blkid_strndup`

Dependencies:
- Public `blkid/blkid.h`
- Local Linux-style `blkid/list.h`

Notable details:
- The cache design is doubly linked and mutable; tag nodes are cross-linked through device lists and per-name head nodes.
- Debug helpers compile only with `CONFIG_BLKID_DEBUG`.
- This header exposes the private implementation shape to all bundled blkid C files.
