# File Research: sources/os/bsd/dragonflybsd/sys/sys/blist.h

Read completely: 134 lines.

This header defines bitmap resource lists, primarily used for swap-style block allocation.

Key contents:
- `swblk_t`/`u_swblk_t` block types and `SWAPBLK_NONE` sentinel.
- `blmeta_t` meta/leaf union plus biggest contiguous block hint.
- `blist_t` root object with total blocks, radix, skip, free count, root pointer, and root coverage.
- Radix constants, maximum block calculations, and maximum allocation size.
- Prototypes for create/destroy, allocate, allocate-at, free, fill/reserve, print, and resize.

Security/reliability notes:
- No implementation here. Tree sizing and overflow limits are central to allocator correctness.
- The comments note conservative maximum sizing because overflow detection is not fully trusted.
