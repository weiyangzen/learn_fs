# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/gfs2l.c

This is the command-line frontend for the small GFS2 metadata language implemented by `lang.c`, `lexer.l`, and `parser.y`.

Behavior:
- Supports `-h`, `-f <script>`, `-T`, and `-F <type>`.
- `-T` prints known metadata structure types sorted by name.
- `-F <type>` prints field offsets and names for one metadata type.
- Opens the target filesystem/device read-write.
- Reads device info, superblock, master directory, and rindex.
- Initializes the language parser, parses the script, iterates results, prints them, and frees state.

Integration role:
- Uses libgfs2 superblock, inode, rindex, metadata table, and language interpreter APIs.
- Provides a direct metadata query/edit tool surface.

Risk notes:
- Opens the filesystem with `O_RDWR`; scripts can modify metadata.
- Some error paths return without closing all descriptors or freeing all state.
- `opts.fspath` is populated but `openfs()` uses `argv[optind]`, so option parsing assumptions matter.
