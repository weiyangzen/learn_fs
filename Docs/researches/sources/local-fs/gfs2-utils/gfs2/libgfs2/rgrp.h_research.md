# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.h

Private resource group helper header.

Defines:
- `struct rg_spec`: resource group length/count plan entry.
- `struct rgs_plan`: flexible-array plan holder.
- `struct _lgfs2_rgrps`: opaque resource group set backing type.
- `struct lgfs2_rbm`: resource group bitmap cursor.
- Inline helpers `rbm_bi()`, `lgfs2_rbm_to_block()`, and `lgfs2_rbm_eq()`.

Exports:
- `lgfs2_rbm_from_block()`
- `lgfs2_rbm_find()`
- `lgfs2_alloc_extent()`

Integration role:
- Used by `rgrp.c` and `fs_ops.c` for extent allocation.

Risk notes:
- `lgfs2_rbm_to_block()` depends on `bi_start` and bitmap-relative offset being consistent.
- `_lgfs2_rgrps` layout is private but must match `libgfs2.h` opaque typedef assumptions.
