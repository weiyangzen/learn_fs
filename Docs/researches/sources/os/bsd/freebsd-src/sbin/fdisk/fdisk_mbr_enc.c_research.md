# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/fdisk_mbr_enc.c

Encodes and decodes packed on-disk MBR partition entries.

Key responsibilities:
- `dos_partition_dec()` copies the 16-byte MBR partition entry byte stream into a native `struct dos_partition`.
- `dos_partition_enc()` writes a native `struct dos_partition` back into the 16-byte MBR entry format.
- Uses `le32dec()` and `le32enc()` for `dp_start` and `dp_size`.

Important fields:
- Byte fields: flag, starting CHS, type, ending CHS.
- Little-endian 32-bit fields: starting LBA and sector count.

Notes:
- The file explicitly performs no validation or sanity checking.
- Intended to be usable in both kernel and userland contexts.
