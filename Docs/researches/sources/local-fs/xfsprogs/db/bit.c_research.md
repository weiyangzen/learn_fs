# File Research: sources/local-fs/xfsprogs/db/bit.c

Provides bit-level extraction and insertion helpers used throughout xfs_db field decoding. `getbit_l` and `setbit_l` address individual bits in big-endian bit numbering within bytes. `getbitval` reads up to 64 bits, using fast unaligned big-endian loads for byte-aligned 8/16/32/64-bit fields and bit scraping otherwise, with optional sign extension. `setbitval` writes arbitrary bit ranges from an input buffer, using `memcpy` only for byte-aligned writes.

This file is foundational for packed btree record fields such as bmbt, rmapbt, and refcountbt records. The code assumes callers pass valid bit widths and object bounds; it asserts `nbits <= 64` for reads.
