# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mapper_std_file.h

Read completely: 75 lines.

This header defines the on-disk standard mapper DB format constants. It declares the magic string, DB symbol names (`type`, `info`, `table`, `rowcol_ext_ilseq`), the `rowcol` type string, current and compatibility row/column info structures, fixed structure sizes, row/column maximum, and out-of-bounds extension modes.

Important interactions: `citrus_mapper_std.c` reads these packed big-endian records from mapped DB regions.

Security/reliability notes: no executable logic. Because these structures are file-format ABI, changes require compatible readers or versioning.
