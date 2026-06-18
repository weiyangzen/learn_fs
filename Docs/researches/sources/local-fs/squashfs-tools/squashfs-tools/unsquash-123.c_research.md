# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-123.c

This helper file provides shared uid/gid table reading for Squashfs 1.x, 2.x, and 3.x compatibility readers.

Key function:
- `read_ids(int ids, long long start, long long end, unsigned int **id_table)`.

Behavior:
- Computes table byte length as `ids * sizeof(unsigned int)`.
- Verifies the computed length equals `end - start`.
- Allocates the output id table.
- Reads raw table bytes from disk.
- Uses `SQUASHFS_SWAP_INTS_3` when the filesystem endian differs from host endian.

Important details:
- The function is for old flat id tables, not the v4 metadata-block indexed id table.
- It assumes callers already validated the number of ids for the relevant version.
- Failure returns `FALSE` after logging an error; partial allocations may remain in some failure paths.
