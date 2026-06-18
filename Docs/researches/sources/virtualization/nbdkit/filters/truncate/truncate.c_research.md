# File Research: sources/virtualization/nbdkit/filters/truncate/truncate.c

This filter presents a per-connection virtual size derived from the underlying export by applying optional `truncate`, `round-up`, and `round-down` operations. Rounding values are parsed as sizes, must be positive, fit in `unsigned`, and be powers of two.

Each connection caches the underlying `real_size` and computed virtual `size` during `.prepare`. Reads inside the real size forward to the backend and reads beyond it are zero-filled. Writes inside the real size are clamped and forwarded; any remaining write beyond the real size must be all zeroes or fails with `ENOSPC`. Trim, zero, and cache similarly clamp to the real backend range and treat tail-only requests as successful no-ops.

The filter always advertises extents and fast zero support after probing the underlying layer. Extents for tail-only ranges are reported as zero/hole; mixed ranges copy underlying extents through a bounded temporary extents list.

Risks and invariants: `truncate_extents` uses the global `truncate_size` when reporting tail length, which matters if the visible size came from only rounding. Dynamic backend resizing is intentionally ignored after prepare. Tail writes of non-zero data are rejected rather than materialized.
