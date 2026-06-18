# File Research: sources/local-fs/jfsutils/xpeek/xpeek.c

Contains the `jfs_debugfs` program entry point, global runtime state, device opening, superblock-derived initialization, and the main command dispatcher.

Global state defined:
- `unsigned type_jfs`: superblock flags used by endian/format logic.
- `int bsize`: aggregate block size.
- `FILE *fp`: opened block device stream used by libfs.
- `short l2bsize`: log2 aggregate block size.
- `int64_t AIT_2nd_offset`: secondary aggregate inode table byte offset.
- `int64_t fsckwsp_offset`: fsck workspace byte offset.
- `int64_t jlog_super_offset`: journal log superblock byte offset.

Startup flow:
- Prints version from `VERSION` and `JFSUTILS_DATE`.
- Emits terminal escape sequence to put console into UTF-8 mode.
- Requires exactly one block device argument.
- Opens the device read/write using `fopen(device, "r+")`.
- Reads primary superblock, falling back to secondary if needed.
- Initializes global block size, log2 block size, superblock flags, secondary AIT offset, fsck workspace offset, and journal log super offset.
- Enters a prompt loop reading commands from stdin.

Command dispatch:
- Prefix-matches commands using the typed command length.
- Dispatches implemented commands: `alter`, `cbblfsck`, `directory`, `dmap`, `dtree`, `xtree`, `display`, `fsckwsphdr`, `help`, `iag`, `inode`, `logsuper`, `superblock`, `s2perblock`, and `quit`.
- Reports unimplemented `btree`, `set`, and `unset`.
- Flushes and closes the device at exit.

Integration points:
- Central user-facing hub for all files in this group.
- Relies on `ujfs_get_superblk`, `ujfs_flush_dev`, PXD address macros, and constants such as `LOGPSIZE`.

Notable behavior and risks:
- Prefix matching allows short abbreviations but can make command ambiguity dependent on ordering and minimum-length guards.
- Opens the device read/write even for display-only use.
- The tool assumes the filesystem is unmounted, but this file does not enforce that.
- If both primary and secondary superblock reads fail, execution jumps to cleanup and returns `0`, not an error status.
