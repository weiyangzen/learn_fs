# File Research: sources/os/plan9/9front/sys/src/cmd/replica/all.h

Shared header for replica tools. Includes Plan 9 libraries and declares the database `Entry`/`Db` structures plus shared helpers.

The database is an AVL-indexed map from logical replica path to metadata: server name, uid, gid, mtime, mode, mark, and length.

Also declares memory/string helpers, `unroot()`, and reverse proto traversal.
