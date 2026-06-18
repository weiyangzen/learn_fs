# File Research: sources/local-fs/jfsutils/tune/super.c

Display helpers for JFS filesystem superblocks and external log superblocks.

Important functions:
- `build_flag_string(...)`: converts `s_flag`/log `flag` bits into readable flag names such as `JFS_LINUX`, `JFS_OS2`, `JFS_GROUPCOMMIT`, `JFS_INLINELOG`, and sparse/DASD flags.
- `display_super(...)`: prints magic, version, state, flags, block sizes, aggregate size, log device, creation time, UUID, label, and external log UUID.
- `display_logsuper(...)`: prints log magic/version, mount serial, block size, size, flags, state, log UUID, label, and active filesystem UUID slots.

Filesystem relevance: read-only inspection formatting for `jfs_tune -l`.
