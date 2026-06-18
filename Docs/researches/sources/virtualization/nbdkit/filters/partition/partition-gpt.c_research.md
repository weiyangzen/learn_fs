# File Research: sources/virtualization/nbdkit/filters/partition/partition-gpt.c

This file locates a selected GPT partition. It reads values from the GPT header using little-endian conversion, validates that partition entries start at LBA 2, then scans the partition-entry array for the non-empty entry matching global `partnum`.

`find_gpt_partition` validates the requested partition number against `nr_partition_entries`, enforces entry sizes between 128 bytes and one sector with exact sector divisibility, and checks that the disk can contain primary and backup partition arrays plus GPT overhead. It reads partition-entry sectors as needed and computes `offset` and `range` from `first_lba` and `last_lba` multiplied by global `sector_size`.

The implementation is intentionally conservative: it rejects non-standard GPT layouts where entries are not adjacent to the header and does not perform full GPT CRC/header validation. It depends on `partition.c` for final disk-boundary validation.
