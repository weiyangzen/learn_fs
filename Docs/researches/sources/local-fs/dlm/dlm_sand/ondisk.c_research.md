# File Research: sources/local-fs/dlm/dlm_sand/ondisk.c

## Purpose
Provides serialization/deserialization helpers for the `dlm_sand` on-disk events format.

## Contents
- `header_copy_out()` / `header_copy_in()` copy event-log header strings and convert all numeric fields between CPU and little-endian format.
- `node_copy_out()` / `node_copy_in()` copy node id, generation, address, node UUID, and boot id.
- `summary_copy_out()` / `summary_copy_in()` serialize `last_all_started_rn`.
- `record_copy_out()` / `record_copy_in()` serialize event records, leaving CRC generation to `record_crc_out()` in `main.c`.

## Dependencies
- Uses structures and constants from `sand_internal.h`.
- Uses byte-order macros from `ondisk.h`.

## Risks / Gaps
- `node_copy_in()` uses `cpu_to_le16()` and `cpu_to_le64()` instead of `le16_to_cpu()` and `le64_to_cpu()`. This is harmless on little-endian systems but wrong for big-endian portability.
- CRC is intentionally not calculated here; callers must remember to call `record_crc_out()` after `record_copy_out()`.
