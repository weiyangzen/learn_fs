# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb_file.c

Parses textual bad block lists from a `FILE *`. `ext2fs_read_bb_FILE2()` reads each line, scans an unsigned block number, rejects values beyond 32 bits with `EOVERFLOW`, validates against filesystem bounds when an fs is provided, and adds valid values to the list.

Invalid in-range parsing lines are skipped; out-of-filesystem block numbers trigger an optional callback with the original bad string.

`ext2fs_read_bb_FILE()` is a compatibility wrapper adapting the older invalid callback signature to the newer `priv_data` form.
