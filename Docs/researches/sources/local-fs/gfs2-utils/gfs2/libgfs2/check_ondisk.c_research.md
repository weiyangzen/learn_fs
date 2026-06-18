# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_ondisk.c

This file contains Check unit tests for superblock on-disk conversion functions.

`check_sb_in()` fills a `struct gfs2_sb` buffer with `0x5a`, calls `lgfs2_sb_in()`, and verifies each relevant `lgfs2_sbd` field individually, including formats, block size, master/root inums, lock protocol/table, and uuid.

`check_sb2_out()` populates an `lgfs2_sbd` with distinct values, calls `lgfs2_sb_out()`, and verifies the resulting `struct gfs2_sb` contains the expected big-endian values and copied fixed-size string/uuid fields.

`suite_ondisk()` groups both tests under “On-disk structure parsing checks”.

The file validates endian conversion and field mapping for the GFS2 superblock. It depends on `libgfs2.h`, GFS2 on-disk structures, and Check.
