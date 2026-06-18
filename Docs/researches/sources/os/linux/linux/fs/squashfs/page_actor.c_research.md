# File Research: sources/os/linux/linux/fs/squashfs/page_actor.c

Implements page actors, the abstraction used by decompressor code to write output either into kmalloc buffers or directly into page-cache pages.

The cache actor simply returns sequential buffer pages. The direct actor maps page-cache pages with `kmap_local_page()` and can return a temporary buffer or `ERR_PTR(-ENOMEM)` when the requested output page is missing.

`handle_next_page()` tracks logical page indexes so holes in the gathered page array are handled without shifting decompressed output.

`squashfs_page_actor_init_special()` allocates a per-page temporary buffer only when the selected decompressor requires one.
