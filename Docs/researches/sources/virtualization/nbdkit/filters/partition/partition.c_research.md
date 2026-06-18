# File Research: sources/virtualization/nbdkit/filters/partition/partition.c

This is the main partition filter that exposes one selected MBR or GPT partition as a virtual disk. It parses required `partition=<PART>` and optional `partition-sectorsize=<512|4096>`, storing global `partnum` and `sector_size`.

`.config_complete` requires a nonzero partition number. `.open` creates a per-connection handle whose `offset`, `range`, and type are filled by `.prepare`. If sector size was not configured, `.prepare` asks the backend for block size and uses 512 or 4096 when the minimum block size matches, otherwise defaults to 512. It validates disk size, reads LBA 0 and 1, chooses GPT if LBA 1 contains `EFI PART` and the disk is large enough, otherwise chooses MBR by boot signature, then calls the helper parser and verifies the resulting partition lies within the disk.

The filter reports an export description including partition number and table type, returns partition `range` as size, and forwards read/write/trim/zero/cache operations with `h->offset` added. Extents are fetched in backend coordinates and translated back to partition-relative offsets.

Notable edge cases include a typo in the invalid sector-size error message (`4086` instead of `4096`), conservative GPT layout requirements in the helper, and reliance on the advertised partition size to keep later I/O bounded.
