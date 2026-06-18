# File Research: sources/os/linux/linux/mm/page_idle.c

Implements Linux idle page tracking through the `/sys/kernel/mm/page_idle/bitmap` binary sysfs file. The bitmap lets privileged userspace mark PFNs idle and later query whether they stayed idle after clearing hardware/software referenced state.

Key responsibilities:
- Creates the `page_idle` sysfs attribute group under `mm_kobj`, exposing a 0600 binary `bitmap` attribute.
- Converts bitmap offsets to PFN ranges using 64-bit chunks and rejects unaligned reads/writes.
- Filters PFNs to online, head, LRU folios via `page_idle_get_folio()`, intentionally ignoring non-user-memory pages.
- On writes, clears current PTE/PMD young state through reverse mapping and marks selected folios idle.
- On reads, rechecks idle folios by clearing PTE/PMD references and MMU notifier young state before reporting a bit as still idle.
- Uses `rmap_walk()` and `page_vma_mapped_walk()` to visit mappings, including PTE-mapped THP and PMD-mapped THP cases.

Important behavior:
- Only LRU folios are tracked because they are safe for reverse-map walking; isolated and non-LRU pages are silently treated as non-idle.
- Referenced mappings clear `folio_idle` and set `folio_young` to avoid confusing reclaim after idle tracking clears access bits.
- The read/write return value is byte progress through completed bitmap chunks, not necessarily the original count if `max_pfn` truncates the request.
- PMD/PTE young clearing is paired with `mmu_notifier_clear_young()` so secondary MMUs participate in access tracking.

Dependencies:
- Relies on page idle flags from `linux/page_idle.h`, page extensions, rmap, `page_vma_mapped_walk()`, MMU notifiers, THP helpers, memory hotplug PFN validation, and sysfs binary attributes.

Notable risks:
- The folio must remain LRU after taking a reference; the helper revalidates this race explicitly.
- Correctness depends on holding the folio lock while walking mappings and on gracefully skipping locked or unmapped folios.
- Bitmap ABI alignment is strict: userspace must use `sizeof(u64)` aligned positions and lengths.
