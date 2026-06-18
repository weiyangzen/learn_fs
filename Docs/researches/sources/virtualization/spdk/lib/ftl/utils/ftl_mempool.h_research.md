# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.h

Header for the FTL fixed-size mempool.

APIs cover:
- DMA-backed pool create/destroy/get/put.
- Externally backed pool create/destroy/initialize.
- Durable-format object claim/release before initialization.
- Pointer/id/index conversion helpers.

The header documents the two-state lifecycle: uninitialized external pools allow claim/release, initialized pools allow get/put.
