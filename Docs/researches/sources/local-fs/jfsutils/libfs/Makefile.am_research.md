# File Research: sources/local-fs/jfsutils/libfs/Makefile.am

Automake source template for the shared static support library.

Key contents:
- Include path: top-level `include`.
- Declares non-installed static library `libfs.a`.
- Lists source modules for device I/O, disk maps, superblocks, inodes, messages, Unicode, endian conversion, open-by-label, journal dump/format/redo/read/map/work, and fsck message definitions.
- Lists internal headers distributed/compiled with the library.

Interactions:
- Produces `../libfs/libfs.a`, linked by `jfs_fscklog` and other utilities.

Research notes:
- Defines libfs as an internal utility archive, not an installed API.
