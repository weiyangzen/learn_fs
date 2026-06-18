# File Research: sources/virtualization/spdk/lib/util/util_internal.h

This private utility header declares shared CRC32 internals.

It defines reflected polynomial constants for IEEE CRC-32 and CRC-32C Castagnoli, defines `struct spdk_crc32_table` with 256 table entries, and declares `crc32_table_init()` and `crc32_update()`.

The header is intentionally internal to `lib/util` CRC implementations. Consumers provide an initialized table and previous CRC value to update partial checksums.
