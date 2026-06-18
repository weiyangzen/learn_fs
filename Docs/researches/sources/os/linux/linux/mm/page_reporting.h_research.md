# File Research: sources/os/linux/linux/mm/page_reporting.h

Internal header connecting the buddy allocator free path to the page reporting worker.

Key responsibilities:
- Declares the `page_reporting_enabled` static key and `page_reporting_order`.
- Declares `__page_reporting_notify()` for the slow notification path.
- Defines `page_reported()` to cheaply test whether reporting is enabled and a page has `PageReported`.
- Defines `page_reporting_notify_free()` for the allocator hot path.
- Provides no-op fallbacks when `CONFIG_PAGE_REPORTING` is disabled.

Important behavior:
- `page_reporting_notify_free()` first checks the static branch, then filters by order before scheduling the expensive reporting path.
- The function is explicitly intended for `__free_one_page()` and keeps the common disabled case minimal.

Dependencies:
- Includes pageblock flags, page isolation, jump labels, slab helpers, page tables, and scatterlist definitions needed by page reporting users.

Notable risks:
- The order threshold controls how often the allocator enters the reporting notification path; too small a threshold increases hot-path overhead.
