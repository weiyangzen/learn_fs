# File Research: sources/os/linux/linux/mm/page_table_check.c

Runtime page-table sanity checker. It uses `page_ext` counters to catch illegal mappings, especially anonymous pages mapped writable more than once or pages simultaneously mapped as anonymous and file-backed.

Key responsibilities:
- Registers `page_table_check_ops` as a page-extension user when enabled by config or the early `page_table_check=` parameter.
- Maintains per-page anonymous and file mapping counters.
- Checks counters when PTE/PMD/PUD entries are cleared or installed.
- Verifies counters are zero when pages are freed or allocated through `__page_table_check_zero()`.
- Exports clear/set hooks used by architecture and generic page-table manipulation code.
- Checks userfaultfd write-protect invariants for present and swap/migration PTE/PMD entries.

Important behavior:
- `init_mm` mappings are ignored.
- Slab pages are invalid for these checks and trigger `BUG_ON()`.
- Anonymous mappings must not coexist with file mappings; writable anonymous mappings must not have a count above one.
- Clear paths decrement counters and assert they do not go negative.
- Set paths clear the old entries first, then increment counters for user-accessible pages across batched PTE/PMD/PUD operations.
- `__page_table_check_pte_clear_range()` walks a PTE page under a non-leaf PMD and clears each PTE's accounting.

Dependencies:
- Uses `page_ext`, page-table helper predicates, swap/softleaf helpers, userfaultfd WP helpers, atomic counters, RCU-protected page extension iteration, and exported static branch state.

Notable risks:
- This checker is intentionally fatal on invariant violations; false positives in page-table helper predicates would crash the kernel.
- Correctness depends on all page-table mutation paths calling the matching clear/set hooks around replacement.
