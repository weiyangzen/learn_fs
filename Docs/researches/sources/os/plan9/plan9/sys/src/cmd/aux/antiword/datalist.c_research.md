# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/datalist.c

This file manages Antiword’s logical data block list and provides sequential binary readers over it.

Key behavior:
- Adds and merges contiguous data blocks mapping logical data positions to physical file offsets.
- Seeks the current data cursor to a physical file offset with `bSetDataOffset()`.
- Reads bytes through a `BIG_BLOCK_SIZE` cache, advancing across linked data blocks.
- Provides little-endian and big-endian word/long readers.
- Skips byte ranges and maps logical data positions back to file offsets.

Important details:
- EOF/error cases set `errno = EIO` because all byte values can be valid data.
- The reader assumes `pBlockCurrent` has been initialized by `bSetDataOffset()`.
- `ulGetDataOffset()` ignores its `FILE *` parameter and reports cursor position from internal state.

Filesystem relevance:
- Direct document-storage mapping: abstracts scattered Word/OLE data blocks as one readable byte stream.
