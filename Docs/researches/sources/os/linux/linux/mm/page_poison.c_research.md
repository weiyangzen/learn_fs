# File Research: sources/os/linux/linux/mm/page_poison.c

Debug page poisoning implementation used by page allocator debugging when architecture debug-pagealloc mapping support is absent or when poisoning is requested. It fills freed pages with `PAGE_POISON` and checks the pattern on allocation.

Key responsibilities:
- Parses the early `page_poison=` boot parameter and exports early/runtime static-key state.
- Poisons pages by locally mapping each page, disabling KASAN checks for the current task, and filling with `PAGE_POISON`.
- Unpoisons pages by checking for bytes that differ from the poison pattern.
- Reports corruption with rate-limited messages, hex dumps, stack dumps, and `dump_page()`.
- Distinguishes a single-bit flip from broader memory corruption for diagnostics.
- Provides a no-op `__kernel_map_pages()` fallback when `CONFIG_ARCH_SUPPORTS_DEBUG_PAGEALLOC` is unavailable.

Important behavior:
- KASAN is temporarily disabled because freed pages are still treated specially by sanitizers.
- The check scans for the first and last corrupted byte so the dump covers the corrupted span only.
- Every page in a multi-page allocation is poisoned or checked independently.

Dependencies:
- Uses highmem local mappings, KASAN tag reset helpers, ratelimit state, `PAGE_POISON`, debug page dumping, and early kernel parameter parsing.

Notable risks:
- Poisoning is diagnostic and expensive; it must stay synchronized with allocator initialization and debug-pagealloc policy.
- Corruption reporting is rate-limited to avoid flooding after widespread memory damage.
