# File Research: sources/local-fs/xfsprogs/db/bmap.c

Implements the `bmap` command and reusable file-offset-to-extent lookup helpers. The core `bmap` function reads the current inode, selects the requested fork, and handles local, extent-list, and btree formats. Extent-list forks are scanned directly; btree forks descend from the inode bmdr root via `select_child`, then scan leaf records and right siblings. `bmap_one_extent` clips returned mappings to the requested file-offset range.

The command can print data and/or attr fork mappings, auto-selecting forks that have extents if no fork option is given. It formats realtime extents differently depending on rtgroup support and prints AG/RT group coordinates. Utility exports include `convert_extent` and `make_bbmap`, which are used by block navigation for multi-extent buffers.
