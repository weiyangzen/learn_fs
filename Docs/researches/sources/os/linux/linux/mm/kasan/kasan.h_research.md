# File Research: sources/os/linux/linux/mm/kasan/kasan.h

Private KASAN header shared by KASAN runtime, reports, quarantine, and tests.

Defines:
- Static-key helpers for stack collection and vmalloc tagging.
- Hardware-tag mode enum and globals.
- Page allocation sampling helpers for hardware-tag mode.
- Mode-dependent `kasan_requires_meta()`, `KASAN_GRANULE_SIZE`, shadow constants, poison values, and metadata layout constants.
- Report structures, compiler ABI structures for globals/source locations, alloc/free metadata, quarantine link, and tag-mode stack ring entries.

Important APIs declared:
- Access checking and reporting: `kasan_check_range()`, `kasan_report()`, invalid-free reporting.
- Metadata/report helpers: allocation size, first bad address, mode completion, metadata rows, tag printing, stack frame printing.
- Slab metadata: alloc/free meta accessors and initialization.
- Stack trace saving and alloc/free info recording.
- Generic quarantine operations, with no-op stubs for non-generic modes.
- Tag helpers: `set_tag()`, `get_tag()`, `kasan_random_tag()`, hardware tag arch wrappers.
- Poison/unpoison primitives and generic-only partial last-granule poisoning.
- KUnit test hooks and compiler-emitted ASAN/HWASAN function declarations.

Role:
This file is the internal ABI contract between compiler instrumentation, architecture tag operations, generic shadow poisoning, KASAN reports, and allocator integration. Several struct layouts and constants are explicitly compiler ABI and must not change casually.
