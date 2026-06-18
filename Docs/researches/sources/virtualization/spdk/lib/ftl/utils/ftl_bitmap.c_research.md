# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.c

Implements a caller-buffer-backed bitmap.

Features:
- Size/block conversion helpers with word alignment.
- Creation validates buffer address and size alignment.
- Get/set/clear by bit index.
- Find-first-set/clear in a range using word scanning and `__builtin_ctzl`.
- Count set bits using `__builtin_popcountl`.

Risk:
- Bounds are enforced by `assert`, so production builds rely on callers passing valid bit ranges.
