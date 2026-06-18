# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenapart.c

Purpose: Prints summary information for every arena in an arena partition.

Key behavior:
- Opens an arena partition read-only/direct, unpacks the arena partition header, computes and reads the arena table, then scans entries.
- For each table entry, reads the arena head and tail, unpacks the tail, and prints arena offset, clump counts, compressed clump counts, used bytes, uncompressed bytes, sealed state, and timestamps.

Dependencies:
- Uses arena partition metadata, arena head/tail unpacking, `partblocksize`, and disk cache initialization.

Notable details:
- Contains a local `rdarena` routine similar to `printarena.c`, but `threadmain` only prints arena summaries and does not call it.
