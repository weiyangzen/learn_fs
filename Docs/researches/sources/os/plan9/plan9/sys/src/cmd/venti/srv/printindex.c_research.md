# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printindex.c

Purpose: Dumps entries from Venti index sections.

Key behavior:
- Loads a Venti config and initializes disk cache.
- Iterates selected or all index sections, reads each index bucket block, unpacks the bucket, unpacks each `IEntry`, and prints address, score, type, and size.

Dependencies:
- Uses index section structures, bucket magic, `unpackibucket`, `unpackientry`, and Plan 9 buffered output.

Notable details:
- `-B` controls disk block cache memory, with a minimum derived from index/arena geometry.
