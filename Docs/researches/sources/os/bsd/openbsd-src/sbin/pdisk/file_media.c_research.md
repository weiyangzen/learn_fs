# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.c

Purpose: Raw media I/O and byte-order conversion layer for `pdisk`. It reads and writes Apple block zero and partition map entries from 512-byte sectors.

On-disk structures:
- Defines byte-array versions of driver map entries, block zero, and DPME partition entries.
- Keeps on-disk representations independent from in-memory `partition_map.h` structs.
- Apple partition data is big-endian on disk; functions copy fields and convert numeric values.

Low-level I/O:
- `read_block()` uses `pread()` for one `DEV_BSIZE` sector at `sector * DEV_BSIZE`, reporting EOF, short read, or read errors.
- `write_block()` uses `pwrite()` for one sector and warns on failure.

Block zero:
- `read_block0()` reads sector 0, decodes signature, block size/count, device type/id/data, driver count, and up to eight driver descriptors.
- `write_block0()` serializes the in-memory block zero fields and driver descriptors back to sector 0.

Partition entries:
- `read_dpme()` reads a DPME sector, converts numeric fields from big endian, copies reserved byte arrays, and NUL-terminates/copies name/type/processor strings into in-memory fields.
- `write_dpme()` serializes strings, reserved fields, and numeric DPME fields to an on-disk byte-array structure and writes the sector.

Integration:
- Implements prototypes from `file_media.h`.
- Used by `partition_map.c` to load and persist the full partition map.
