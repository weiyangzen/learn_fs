# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/alloc.c

Defines `nbemalloc`, the NetBIOS allocation wrapper.

Key behavior:
- Calls `malloc`.
- On allocation failure, prints an error and exits all threads with status `mem`.

Interactions:
- Used throughout NetBIOS and SMB support as the lower-level fatal allocator.
- `smballoc.c` builds SMB allocators on top of it.

Notable details:
- Does not zero memory; callers requiring zeroing use wrappers such as `smbemallocz` or `mallocz`.
