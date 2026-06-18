# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/all.h

Read status: complete, 70 lines.

This shared header for `replica` includes Plan 9 system headers and declares the replica support APIs. It defines the embedded `Avl` node, opaque AVL tree/walk types, database entry structures, and database operations.

`Entry` records a replica path plus metadata: stored name, uid, gid, mtime, mode, mark flag, and length. `Db` wraps an AVL tree and backing file descriptor.

It also declares allocation/string helpers and the reverse proto reader `revrdproto`.

Filesystem relevance: defines the metadata model used by replica database scanning and synchronization.
