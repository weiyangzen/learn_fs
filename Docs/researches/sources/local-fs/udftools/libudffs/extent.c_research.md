# File Research: sources/local-fs/udftools/libudffs/extent.c

Implements in-memory extent, descriptor, and data-list management for UDF construction.

The file begins with an extensive explanation of:
- Volume space versus partition space.
- ECMA on-disk extents versus in-memory `udf_extent`.
- How extents, descriptors, and data payloads compose the planned output.

Main functions:
- `next_extent`, `prev_extent`: scan extent lists by space type.
- `next_extent_size`, `find_next_extent_size`, `prev_extent_size`: find aligned free/typed extents of sufficient size.
- `find_extent`: find the extent containing a block.
- `set_extent`: split existing extents and assign a type to a requested range.
- `remove_extent`: unlink and free an extent.
- `next_desc`, `find_desc`, `set_desc`: maintain ordered descriptor lists within an extent.
- `append_data`: append payloads to a descriptor and grow length.
- `alloc_data`: allocate a `udf_data` wrapper and optional zeroed payload.

Error handling:
- Allocation failures and out-of-space conditions print with `appname` and call `exit(1)`.

Key role: shared allocator/planner primitive used heavily by mkudffs structure generation.
