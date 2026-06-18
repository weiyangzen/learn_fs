# File Research: sources/virtualization/nbdkit/filters/cow/cow.c

Purpose: nbdkit copy-on-write filter that makes a read-only backend appear writable by storing changes in temporary overlays.

Key details:
- Configures `cow-block-size`, `cow-on-cache`, and `cow-on-read`.
- Keeps a global mapping from export name to `blk_overlay`, so connections to the same export share one overlay.
- Opens the backend read-only regardless of requested mode.
- `.get_size` initializes overlay size to backend size; `.prepare` forces this early.
- Advertises write, trim, flush, extents, FUA, cache, fast-zero, and multi-connection support.
- `.pread` reads from overlay, backend, or zero-filled trimmed blocks through `blk_read*`.
- `.pwrite` writes full blocks directly to overlay and serializes unaligned read-modify-write through `rmw_lock`.
- `.zero` writes zero-filled blocks into overlay; fast zero is rejected with `ENOTSUP`.
- `.trim` marks aligned blocks trimmed and handles unaligned edges as zero writes.
- `.flush` is deliberately ignored because overlay data is temporary.
- `.cache` maps backend cache support to block cache behavior, optionally copying cache requests into the overlay.
- `.extents` combines overlay bitmap state with backend extents, reporting trimmed overlay blocks as hole+zero.

Risk notes:
- FUA/flush are intentionally ignored, so durability is only in-process temporary overlay lifetime.
- Export-name overlay sharing is useful for multi-connection consistency but means overlay memory/temp usage persists until filter unload.
