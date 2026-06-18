# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_chunk_upgrade.c

Defines NV cache chunk metadata upgrade from v1 to v2.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v2 chunk metadata region sized for `chunk_count`.
- Initializes every v2 chunk metadata entry with `ftl_nv_cache_chunk_md_initialize()`.
- Persists the new region and completes layout upgrade.

Important assumption:
- Comments state chunks should be fully drained of user data before this major upgrade, so old metadata contents are not interpreted.
