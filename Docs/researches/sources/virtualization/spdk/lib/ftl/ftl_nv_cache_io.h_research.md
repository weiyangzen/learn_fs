# File Research: sources/virtualization/spdk/lib/ftl/ftl_nv_cache_io.h

Provides two inline wrappers for NV-cache block IO with optional metadata:
- `ftl_nv_cache_bdev_read_blocks_with_md`
- `ftl_nv_cache_bdev_write_blocks_with_md`

Each wrapper checks whether the underlying bdev exposes metadata via `spdk_bdev_get_md_size`. If metadata exists, it calls the SPDK `_with_md` API and substitutes global fallback buffers (`g_ftl_read_buf` or `g_ftl_write_buf`) when the caller passes `NULL` metadata. If no metadata exists, it calls the plain block read/write API.

Architectural role: this isolates NV-cache IO callers from metadata-capable versus data-only bdev differences and keeps call sites in compaction, chunk tail metadata, and user reads simpler.
