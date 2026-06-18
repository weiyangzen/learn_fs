# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/file_media.h

Purpose: Public media I/O interface for `pdisk`.

Declared API:
- `read_block0(int, struct partition_map *)`
- `write_block0(int, struct partition_map *)`
- `read_dpme(int, uint64_t, struct entry *)`
- `write_dpme(int, uint64_t, struct entry *)`

Integration:
- Consumed by partition map management code.
- Relies on `struct partition_map` and `struct entry` declarations from `partition_map.h`.
