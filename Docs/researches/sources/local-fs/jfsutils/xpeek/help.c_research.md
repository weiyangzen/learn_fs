# File Research: sources/local-fs/jfsutils/xpeek/help.c

Implements textual help for `jfs_debugfs`.

Main entry point:
- `help(void)`: accepts zero or one command argument.
- With no argument, prints a full command list.
- With a command prefix, prints command-specific syntax and short explanations.

Covered commands:
- `alter`, `btree`, `cbblfsck`, `directory`, `dtree`, `display`, `dmap`, `fsckwsphdr`, `help`, `iag`, `inode`, `logsuper`, `quit`, `set`, `superblock`, `s2perblock`, `unset`, and `xtree`.

Integration points:
- Uses the same prefix-matching convention as `xpeek.c`.
- Documents some commands that are not implemented or only partially implemented in the dispatcher, such as `btree`, `set`, and `unset`.

Notable behavior and risks:
- Help advertises some `display` formats (`b`, `d`) that are not implemented in `display.c`.
- Help text for `s2perblock` prints `su[perblock] [p | s]`, likely a typo.
- Some messages contain spelling errors inherited from original utility text, such as “aggragate”.
