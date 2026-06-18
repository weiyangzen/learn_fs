<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh

Purpose: Implements a simple path-to-value map optimized for longest-prefix matching.

APIs and control flow: The anchor/default constructor creates a head node. `Insert()` places nodes in decreasing path-length order. `Find()` looks for an exact path and can stop early because of that ordering. `Match()` returns the first stored path that prefixes a supplied pathname. Accessors expose name, path, next node, and value, while `RepName()` and `RepValu()` mutate stored metadata.

State and persistence: Each node owns duplicated `Path` and `Name` strings and stores a template value `T`. The list has no locking, persistence, or copy-control.

Dependencies and integration: Uses C string allocation and comparison from libc. It is suitable for configuration maps where longer mount or namespace prefixes must win.

Risks and test signals: Prefix matching does not enforce path-component boundaries, so `/foo` matches `/foobar`. `RepName()` checks `Path` before freeing `Name`, which is unusual but harmless for normal nodes. Tests should cover exact lookup, ordering, empty anchors, overlapping prefixes, and destruction ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucMapP2X.hh -->
