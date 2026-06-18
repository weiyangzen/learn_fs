# File Research: sources/os/linux/linux/mm/kasan/hw_tags.c

Hardware tag-based KASAN runtime, mainly for architectures with memory tagging such as arm64 MTE.

Boot parameters:
- `kasan=off|on`
- `kasan.mode=sync|async|asymm`
- `kasan.vmalloc=off|on`
- `kasan.write_only=off|on`
- `kasan.page_alloc.sample=<interval>`
- `kasan.page_alloc.sample.order=<order>`

Core behavior:
- `kasan_init_hw_tags_cpu()` enables tag checks on each MTE-capable CPU unless KASAN is disabled.
- `kasan_init_hw_tags()` verifies hardware support, applies boot parameter selections, initializes tags, enables KASAN, and prints mode/vmalloc/stacktrace/write-only state.
- `kasan_enable_hw_tags()` selects sync/async/asymmetric hardware tag checks and attempts write-only mode when requested.
- Page allocation sampling state is exposed through globals and per-CPU skip counters.

Vmalloc handling under `CONFIG_KASAN_VMALLOC`:
- Only VM_ALLOC mappings with normal protections are tagged.
- Non-VM_ALLOC and executable mappings are left untagged.
- `__kasan_unpoison_vmalloc()` assigns/reuses a tag, unpoisons valid bytes, poisons in-page redzone, and stores page tags so direct page access works.
- `__kasan_poison_vmalloc()` does not retag because backing pages follow page-allocator paths.

KUnit exports provide hooks to force async faults and query write-only mode.
