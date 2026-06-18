# File Research: sources/os/linux/linux/mm/kasan/kasan_test_c.c

KUnit test suite for KASAN bug-detection capabilities across generic, software-tag, and hardware-tag modes.

Harness:
- Suite init refuses to run if KASAN is disabled.
- Enables KASAN KUnit test mode and temporary multi-shot reporting.
- Registers a console trace probe to detect `BUG: KASAN:` and asynchronous fault messages.
- `KUNIT_EXPECT_KASAN_RESULT()` runs expressions, handles hardware-tag sync fault re-enable, optionally forces async faults, and compares observed reports with expectation.
- Helpers skip tests depending on config and checked memintrinsic availability.

Coverage areas:
- kmalloc/slab/page allocation out-of-bounds, use-after-free, invalid free, double free, `krealloc()`, `ksize()`, and `kfree_sensitive()`.
- memcpy/memset/memmove and string/memchr/memcmp instrumentation.
- Atomics and bitops instrumentation.
- RCU/workqueue auxiliary stack reporting.
- Custom kmem caches, `SLAB_TYPESAFE_BY_RCU`, cache destruction, memcg accounted caches, and bulk allocation.
- Mempool poisoning for kmalloc, large kmalloc, slab, and page pools.
- Global, stack, and dynamic alloca redzones.
- vmalloc/vmap/vm_map_ram tagging and vmalloc OOB behavior.
- Tag-mode properties: non-assignment of match-all tags, match-all pointer tag behavior, and absence of match-all memory tags.
- Rust UAF smoke test through `kasan_test_rust_uaf()`.
- `copy_to_kernel_nofault()` when built-in and copy-to/from-user instrumentation.

Test list:
The `kasan_kunit_test_cases[]` table registers all scenarios and marks atomics as slow. The suite is named `kasan`.

Important nuance:
Many tests are mode-specific because generic KASAN has byte-precise shadow and quarantine, while tag-based modes use granule tags and may not precisely detect unaligned or adjacent-object cases.
