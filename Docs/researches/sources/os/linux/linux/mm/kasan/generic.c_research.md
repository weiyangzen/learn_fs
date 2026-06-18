# File Research: sources/os/linux/linux/mm/kasan/generic.c

Core Generic KASAN runtime.

Main functionality:
- `kasan_init_generic()` enables KASAN after architecture shadow setup.
- Inline shadow checks implement fast validation for 1, 2, 4, 8, 16, and variable-size accesses.
- `kasan_check_range()` validates address metadata, overflow, zero size, and poisoned shadow state.
- Exports compiler ABI entry points: `__asan_load*`, `__asan_store*`, `__asan_loadN`, `__asan_storeN`, and noabort aliases.
- Handles compiler-emitted alloca poisoning/unpoisoning and shadow byte setters.
- Registers global variables by unpoisoning the object and poisoning global redzones.
- Computes adaptive slab redzone sizes and lays out KASAN allocation/free metadata.
- Saves allocation/free stack metadata and auxiliary stacks.

Important metadata logic:
- `kasan_cache_create()` marks caches with `SLAB_KASAN | SLAB_NO_MERGE`, adds alloc/free metadata when possible, and grows object size to include adaptive redzones.
- Free metadata may live inside the object or in the redzone depending on object size, constructor, `SLAB_TYPESAFE_BY_RCU`, and SLUB debug.
- `KASAN_SLAB_FREE_META` shadow byte marks valid free metadata.

Role:
This file is the byte-precise shadow-memory KASAN engine. Tag-based modes use different access-check mechanisms and do not use this metadata/quarantine-heavy layout.
