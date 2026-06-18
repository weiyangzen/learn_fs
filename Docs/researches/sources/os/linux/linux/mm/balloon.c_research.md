# File Research: sources/os/linux/linux/mm/balloon.c

## Purpose
Provides common helper code for memory balloon drivers, including balloon page allocation, enqueue/dequeue accounting, and optional migration support for inflated balloon pages.

## Main Interfaces
- Allocation and list operations: `balloon_page_alloc()`, `balloon_page_enqueue()`, `balloon_page_dequeue()`.
- Batched operations: `balloon_page_list_enqueue()`, `balloon_page_list_dequeue()`.
- Migration hooks under `CONFIG_BALLOON_MIGRATION`: isolate, putback, and migrate operations registered for offline movable pages.

## Control Flow
Drivers allocate pages with balloon-appropriate GFP flags, enqueue them into the balloon device list, and later dequeue them before returning pages to the guest allocator. Enqueue marks pages offline, optionally installs movable ops and `page_private` backpointer, adjusts managed page counts, and updates balloon VM/node counters. Dequeue reverses accounting and finalizes pages for release.

With migration enabled, compaction can isolate balloon pages, call the driver-specific `migratepage()` callback, insert the replacement page into the balloon list on success, or account deflation when migration reports `-ENOENT`.

## State And Synchronization
A global `balloon_pages_lock` protects balloon page lists, `page_private` balloon ownership, and isolated-page counters. Page offline state remains sticky until returned to the buddy allocator.

## Integration Points
Used by virtualization balloon drivers through `struct balloon_dev_info`. Hooks into MM migration through `movable_operations`, VM event counters, node page state, and optional managed page count adjustment.

## Risks And Review Focus
- Drivers must not use `page->lru` while a page is enqueued.
- Dequeue can return `NULL` while pages are temporarily isolated by compaction.
- Migration callback results affect whether old and new pages are counted as inflated or deflated.
