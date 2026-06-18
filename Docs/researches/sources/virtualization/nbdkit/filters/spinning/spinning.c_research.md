# File Research: sources/virtualization/nbdkit/filters/spinning/spinning.c

This file implements the `spinning` filter, which makes an export behave like a rotational disk by inserting seek latency before reads, writes, and zero requests. It advertises `.is_rotational = 1` and disables `.can_multi_conn` because each NBD connection currently has an independent view of head positions.

Configuration supports `heads`, `separate-heads`, `min-seek-time`, `half-seek-time`, and `max-seek-time`. Completion derives a quadratic seek-time curve through the configured minimum, half-stroke, and full-stroke times and validates that it reproduces the three configured points.

Per-connection state records export size and a vector of head ranges. `.prepare` splits the export across up to 64 heads, initializes per-head mutexes, and reduces head count for tiny exports. `do_seek` finds the responsible head by offset, locks either that head or head 0 depending on `separate-heads`, updates simulated positions, and sleeps when movement exceeds `TRACK_SIZE`.

Risks and invariants: the vector search assumes non-empty, ordered head ranges; zero-sized exports produce zero heads and would make request paths unsafe if invoked. Holding the head lock during sleep intentionally serializes seek behavior. The computed delay can be negative if users configure unusual timing, and negative delays are skipped.
