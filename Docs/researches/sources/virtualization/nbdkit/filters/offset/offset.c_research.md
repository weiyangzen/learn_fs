# File Research: sources/virtualization/nbdkit/filters/offset/offset.c

This filter exposes a byte subrange of the underlying plugin. Configuration parses `offset=OFFSET` and optional `range=LENGTH` through `nbdkit_parse_size`.

`.get_size` validates that `offset` and `range` lie within the backend size and returns either the configured range or the remaining backend size after the offset. Read, write, trim, zero, and cache callbacks simply add the configured offset before forwarding to `next`.

The extents handler allocates a temporary extents list over the backend coordinate range, delegates to `next->extents`, subtracts the configured offset from each returned extent, and adds translated extents to the caller's list.

Main correctness concerns are integer-boundary checks in `get_size` and extent end calculation when `range` is unset; the filter relies on nbdkit bounds checking for individual requests once the advertised size is correct.
