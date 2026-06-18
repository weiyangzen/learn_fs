# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstypes.h

Defines common Ghostscript library scalar and geometry types used throughout the graphics core.

Key definitions:
- `gs_id` and `gs_no_id` for internally generated unique IDs, especially for cached bitmap-like objects.
- Mutable and const string records with explicit `data` and `size`, avoiding C string limitations for binary data and substrings.
- Parameter strings with a `persistent` lifetime flag.
- Mutable and const byte-string wrappers that can either reference raw strings or byte objects for garbage-collection tracking.
- Point, integer point, log2 scale point, rectangle, integer rectangle, and closed floating range structures.

Research notes:
- Rectangle comments explicitly define `gs_rect` and `gs_int_rect` as half-open intervals.
- `gs_range_t` is explicitly closed, unlike the rectangle interval types.
