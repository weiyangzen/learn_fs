# File Research: sources/os/linux/linux-stable/fs/gfs2/meta_io.h

Declares metadata I/O helpers and small buffer manipulation utilities.

Key contents:
- Inline helpers clear whole buffers, clear tails, and copy/zero buffer tails.
- Exposes `gfs2_meta_aops` and `gfs2_rgrp_aops`.
- Provides `gfs2_mapping2sbd()` for mapping metadata or inode address spaces back to `struct gfs2_sbd`.
- Declares metadata buffer creation/read/wait/get, journal wipe, typed metadata buffer lookup, and readahead APIs.
- Defines `REMOVE_JDATA` and `REMOVE_META` modes for journal removal.
- Defines `buffer_busy()` as dirty, locked, or pinned.

Callers use this header for safe metadata buffer access under glock protection. The major contract is that returned buffer heads carry references and must be released by callers.
