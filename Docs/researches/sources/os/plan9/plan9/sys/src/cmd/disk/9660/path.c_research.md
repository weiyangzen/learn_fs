# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/path.c

Writes ISO 9660 path tables after directory data has been written.

`writepathtable` starts from the root directory entry in a volume descriptor, writes path table entries breadth-first, and uses the path table itself as the traversal queue. Because path entries do not include directory lengths, it keeps a parallel in-memory length array. It reads directory blocks to discover subdirectories and writes either little-endian or big-endian table entries.

`writepathtablepair` writes little and big path tables for one descriptor and patches descriptor path-table fields with `setpathtable`. `writepathtables` writes ISO tables and, if present, Joliet tables.

Integration points: called near the end of `dump9660.c` after root descriptors are patched.

Risks and notes: comments explicitly reject padding path table entries across block boundaries despite the rest of ISO’s block-alignment style, for Windows compatibility. Traversal relies on valid previously written directory records.
