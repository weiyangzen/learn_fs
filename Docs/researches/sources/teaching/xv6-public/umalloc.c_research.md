# File Research: sources/teaching/xv6-public/umalloc.c

User-space malloc/free implementation from K&R.

Key behavior:
- Uses a circular free list of `Header` units aligned by `long`.
- `free` inserts a block in address order and coalesces adjacent blocks.
- `morecore` requests memory from `sbrk`, at minimum 4096 header units.
- `malloc` finds a first-fit block, splits from the tail when larger than needed, or asks `morecore`.

Role:
- Provides dynamic allocation for the shell parser and tests.
