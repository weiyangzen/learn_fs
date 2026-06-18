# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_extent.h

Read completely: 64 lines.

Defines EFS extent descriptors. `struct efs_dextent` represents the packed on-disc 8-byte bitfield-like format with an 8-bit magic value, 24-bit filesystem block number, 8-bit length, and 24-bit logical file offset.

Because portable C bitfield layout is unreliable, the implementation accesses `ex_bytes` and `ex_words` and converts to `struct efs_extent`, an in-core unsquished representation with normal integer fields.

Constants define the expected extent magic value, masks for 24-bit fields, and the number of extent descriptors per 512-byte basic block.
