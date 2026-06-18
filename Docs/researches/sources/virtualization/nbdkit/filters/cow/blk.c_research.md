# File Research: sources/virtualization/nbdkit/filters/cow/blk.c

Purpose: block-level sparse overlay implementation for the COW filter.

Key details:
- Uses unlinked temporary files as sparse overlays.
- Splits overlays into multiple files when virtual size exceeds `MAX_FILE_SIZE` of 8 TiB.
- Maintains a two-bit bitmap per overlay block: not allocated, allocated, or trimmed.
- `blk_create` initializes the first temporary file, mutex, and bitmap.
- `blk_set_size` resizes bitmap and overlay file vector, creating/removing temp files as needed and truncating each file.
- `blk_status` exposes overlay presence/trim state to extent synthesis.
- `blk_read_multiple` groups runs with identical bitmap state and same temp-file shard; reads backend, overlay, or returns zeroes for trimmed blocks.
- Optional cow-on-read writes backend-read data into overlay and marks blocks allocated.
- `blk_cache` can ignore, pass through backend cache, read backend, or copy backend data into the overlay depending on cache mode.
- `blk_write` writes a whole block into the correct overlay shard and marks allocated.
- `blk_trim` marks a whole block as trimmed without punching holes.

Risk notes:
- Some bitmap updates in cow-on-read happen after a backend read and temp write; concurrent reads/writes rely on documented ordering rather than broad serialization.
