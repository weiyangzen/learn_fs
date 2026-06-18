# File Research: sources/virtualization/spdk/lib/env_ocf/mpool.h

Declares the OCF environment multi-pool API.

Important contents:
- Defines allocation orders `env_mpool_1` through `env_mpool_128`.
- Forward-declares `struct env_mpool`.
- Declares create/destroy/new/delete operations.
- `env_mpool_create()` accepts fixed header size, per-element size, max order, fallback mode, per-order limits, name prefix, and zeroing flag.

Note: the parameter name is spelled `name_perfix` in the declaration, while the implementation uses `name_prefix`; this is harmless C API spelling drift.
