# File Research: sources/virtualization/nbdkit/filters/delay/delay.c

Purpose: injects configurable latency into nbdkit operations.

Key details:
- Supports separate delays for read, write, zero, trim/discard, extents, cache, open, and close/finalize.
- Historical `wdelay` sets write, zero, and trim delays together.
- `delay-trigger` makes delays conditional on a file existing.
- Uses `nbdkit_parse_delay` for duration parsing.
- `.open` delays before opening backend; `.finalize` delays well-behaved disconnects using `nanosleep`.
- `.pread`, `.pwrite`, `.zero`, `.trim`, `.extents`, and `.cache` delay then delegate.
- `delay-fast-zero=false` causes delayed fast-zero requests to fail quickly with `ENOTSUP` instead of sleeping.

Risk notes:
- Close delay cannot affect clients that simply drop the connection; comments explicitly call out this limitation.
