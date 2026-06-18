# File Research: sources/local-fs/jfsutils/xpeek/xpeek.h

Common header for the `xpeek`/`jfs_debugfs` utility. It declares shared globals, status constants, and cross-file function prototypes.

Definitions:
- `AGGREGATE_2ND_I -1`: selector for the secondary aggregate inode table.
- `XPEEK_OK`, `XPEEK_CHANGED`, `XPEEK_REDISPLAY`, `XPEEK_ERROR`: shared return/status flags for interactive editor flows.

Shared globals:
- `extern int bsize`.
- `extern FILE *fp`.
- `extern short l2bsize`.

Declared APIs:
- Commands: `alter`, `cbblfsck`, `directory`, `display`, `dmap`, `dtree`, `help`, `fsckwsphdr`, `iag`, `inode`, `logsuper`, `superblock`, `s2perblock`, `xtree`.
- Display helpers: `display_iag`, `display_inode`, `display_super`.
- Lookup helpers: `find_iag`, `find_inode`.
- UI helpers: `m_parse`, `more`, `prompt`.
- I/O helpers: `xRead`, `xWrite`.

Included JFS structures:
- `jfs_types.h`, `jfs_dinode.h`, `jfs_imap.h`, and `jfs_superblock.h`.

Notable behavior and risks:
- Defines `#define fputs(string,fd) { fputs(string,fd); fflush(fd); }`, wrapping all subsequent `fputs` calls in including translation units to force flushing. This is unusual, can surprise maintainers, and shadows the C library function name.
- Prototype `void s2perblock(void);` does not match the implementation name `superblock2(void)` used by `xpeek.c`.
- The header centralizes many unrelated command prototypes, reflecting the utility’s tightly coupled design.
