# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_self_test.c

Defines optional startup validation enabled by the `FTL_SELF_TEST` environment variable. The test scans the full L2P in 4096-LBA pinned windows and compares it against `dev->valid_map`.

Important behavior:
- Allocates a temporary bitmap covering base plus NV cache blocks.
- For every non-invalid L2P address, rejects duplicate physical references.
- Checks that every mapped physical address is set in the device valid map.
- Compares counted temporary valid references with `ftl_bitmap_count_set(dev->valid_map)`.

Risk:
- Intended for debugging only; it loads/checks the whole L2P and can be expensive.
- Cleanup is represented both as step cleanup and explicit final cleanup, so ownership depends on normal management-process cleanup semantics.
