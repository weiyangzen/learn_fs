# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/compactdb.c

Read status: complete, 42 lines.

`replica/compactdb` rewrites a replica database in compact canonical form. It opens the database, walks the AVL tree in sorted order, and prints each live entry to stdout.

Removed tombstones and superseded entries are naturally omitted because `opendb` replays the append-only database into current in-memory state first.

Filesystem relevance: maintenance tool for replica metadata databases, reducing append-only log growth.
