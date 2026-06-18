# File Research: sources/local-fs/f2fs-tools/fsck/dict.h

## Purpose
Public API and data structure declarations for the embedded Kazlib red-black-tree dictionary.

## Key structures
- `dnode_t`:
  - left/right/parent pointers
  - red/black color
  - key pointer
  - data pointer
- `dict_t`:
  - embedded nil sentinel
  - node count and max count
  - compare function
  - allocator/free callbacks and context
  - duplicate-key flag
- `dict_load_t`:
  - bulk-load helper state for sorted loading when compiled in.

## Key API groups
- Create/init/destroy/free:
  - `dict_create`, `dict_init`, `dict_destroy`, `dict_free_nodes`, `dict_free`
- Lookup/order:
  - `dict_lookup`, `dict_lower_bound`, `dict_upper_bound`, `dict_first`, `dict_last`, `dict_next`, `dict_prev`
- Mutation:
  - `dict_insert`, `dict_delete`, `dict_alloc_insert`, `dict_delete_free`, `dict_merge`
- Node:
  - `dnode_create`, `dnode_init`, `dnode_destroy`, `dnode_get`, `dnode_getkey`, `dnode_put`
- Utilities:
  - `dict_allow_dupes`, `dict_count`, `dict_isempty`, `dict_isfull`, `dict_contains`, `dict_verify`

## Conditional behavior
When structures are not opaque, the header defines direct macro accessors for count/empty/full and node get/put/key operations. `DICT_IMPLEMENTATION` exposes internal layout to `dict.c`.

## Research notes
This header presents the full Kazlib API, but normal `dict.c` compilation in this tree disables several corresponding implementations. Treat the header as broader than the currently linked fsck subset.
