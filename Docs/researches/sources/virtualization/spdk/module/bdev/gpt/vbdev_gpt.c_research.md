# File Research: sources/virtualization/spdk/module/bdev/gpt/vbdev_gpt.c

## Purpose
Implements the GPT virtual bdev module. It examines bdevs for SPDK GPT partitions and exposes each matching partition as a `spdk_bdev_part`.

## Main Entry Points
- `vbdev_gpt_examine()` screens bdev geometry and starts GPT reads.
- `vbdev_gpt_read_gpt()` creates base context and reads the primary GPT window.
- `gpt_bdev_complete()` parses MBR/primary GPT and falls back to secondary GPT if needed.
- `gpt_read_secondary_table_complete()` parses secondary GPT and creates partition bdevs.
- `vbdev_gpt_submit_request()` forwards partition I/O to the base bdev, acquiring buffers for reads.

## Internal Mechanics
`gpt_base` owns the parser buffer, a bdev part base, the partition list, and a temporary channel used only during table reads. Created GPT partition bdevs are named `<base>p<N>` with one-based partition indices, carry the partition unique GUID as bdev UUID, and expose JSON info containing base name, offset, table GUID, partition type GUID, unique GUID, and UTF-16LE partition name.

Only partitions with SPDK's current type GUID or deprecated old type GUID are exposed. The old GUID deliberately subtracts one block from the partition size to preserve compatibility with historical layouts. Partitions outside the GPT usable LBA range are ignored.

I/O forwarding uses `spdk_bdev_part_submit_request()`. On `-ENOMEM`, the request is queued with `spdk_bdev_queue_io_wait()` and resubmitted later. Memory domain support is forwarded from the base bdev unless DIF reference-tag checking is enabled, because bdev_part must touch metadata in that case.

## Dependencies
Uses SPDK bdev module/partition helpers, env/thread/RPC/string utilities, endian helpers, and parser functions from `gpt.c`.

## Risks and Notes
The module only examines bdevs with at least two blocks and block size divisible by 512. If no partitions are created, it frees the part-base context after examine completion. Secondary GPT fallback reads the last `gpt->buf_size` bytes; unusual layouts must fit the module's buffer assumptions.
