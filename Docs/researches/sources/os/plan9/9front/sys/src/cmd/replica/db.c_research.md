# File Research: sources/os/plan9/9front/sys/src/cmd/replica/db.c

Append-only replica database implementation. Loads records into an AVL tree keyed by logical name, handles tombstone records marked `REMOVED`, and appends insert/remove records back to the backing fd.

Uses a small free-list allocator for `Entry`. Public operations: `opendb`, `finddb`, `markdb`, `insertdb`, and `removedb`.

`markdb()` is used by walkers to identify database entries visited in the current scan.
