# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tdbtool.c

Interactive and command-line utility for inspecting and modifying TDB databases. It is imported from Samba tooling and uses the bundled `tdb.h` API.

Commands include create, open, erase, dump, insert, move, store, show, keys, hexkeys, delete, list hash/free chains, free, info, first/next iteration, shell escape, help, and quit. The tool can open a database passed as argv[1], then either run interactively or execute a command from argv.

It prints records as ASCII plus hex dumps, supports escaped byte input through backslash hex parsing, traverses for summary byte counts, and can move a record into another TDB. The `erase` command deletes records during traversal. The `!` command passes text to `system`, so this is a developer/debug utility rather than a constrained parser.
