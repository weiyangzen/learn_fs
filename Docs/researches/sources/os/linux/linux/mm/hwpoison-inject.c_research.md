# File Research: sources/os/linux/linux/mm/hwpoison-inject.c

Debugfs module for injecting software-simulated hardware memory poison into an arbitrary PFN.

Interfaces created under debugfs `hwpoison/`:
- `corrupt-pfn`: write PFN to call `memory_failure(pfn, MF_SW_SIMULATED)`.
- `unpoison-pfn`: write PFN to call `unpoison_memory()`.
- Filter controls for enable, device major/minor, page flags mask/value, and memcg inode when `CONFIG_MEMCG` is enabled.

Key behavior:
- Injection requires `CAP_SYS_ADMIN` and a valid PFN.
- Optional filtering can restrict targets by backing device, stable page flags, and memcg.
- When filters are active, it calls `shake_folio()` and only proceeds for LRU folios, hugetlb folios, or free buddy pages.
- A racy precheck is used before `memory_failure()`, which then repeats reliable checks under proper locking.
- `-EOPNOTSUPP` from `memory_failure()` is converted to success for testing convenience.

Dependencies:
- Uses internal memory-failure hooks declared in `mm/internal.h`: `hwpoison_filter_register()`, `hwpoison_filter_unregister()`, and `shake_folio()`.
