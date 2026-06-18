# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/db.c

Read status: complete, 181 lines.

This file implements the replica metadata database. The backing file is append-only text; `opendb` replays it into an AVL tree keyed by path. Entries have seven fields: path, stored name, mode or `REMOVED`, uid, gid, mtime, and length.

`insertdb` appends a quoted metadata line and updates the in-memory AVL. `removedb` appends a tombstone line and deletes the AVL entry. `finddb` and `markdb` retrieve metadata, with `markdb` setting the in-memory mark bit used during scans.

`allocentry` uses a small free-list allocator for `Entry` objects. String values are atomized by `util.c`, allowing shared stable pointers.

Filesystem relevance: core persistent state for replica tools, tracking file identity and metadata across synchronization runs.
