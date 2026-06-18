# File Research: sources/os/linux/linux/mm/page_reporting.c

Free page reporting core. It lets one registered device driver receive batches of free pages so the platform can mark them unused, discard them, or otherwise report them to a host, while returning the pages to the buddy allocator afterward.

Key responsibilities:
- Provides the `page_reporting_order` module parameter and exported symbol.
- Maintains a single RCU-protected registered `page_reporting_dev_info`.
- Enables the allocator hot-path static key used by `page_reporting_notify_free()`.
- Schedules delayed reporting work after suitable free pages are observed.
- Walks zones, orders, and migratetypes to isolate unreported free pages into scatterlists.
- Calls the registered device `report()` callback on full or leftover scatterlists.
- Puts isolated pages back and marks them `PageReported` when reporting succeeds and the page was not coalesced into a different order.
- Supports unregister by removing the RCU pointer and canceling delayed work.

Important behavior:
- The worker has three visible states: idle, requested, and active; requests during an active pass cause another delayed pass.
- Work is delayed by two seconds to accumulate a useful batch and avoid excessive reporting frequency.
- Zone processing requires enough free memory above a low-watermark plus reporting-capacity reserve before it will pull pages.
- Isolated pages are not taken from `MIGRATE_ISOLATE` freelists.
- Each freelist pass has a budget based on the freelist size, preventing one list from monopolizing the worker.
- The zone lock is dropped while invoking the device callback and reacquired to drain pages back to the allocator.

Dependencies:
- Uses buddy free areas, pageblock migratetypes, `__isolate_free_page()`, `__putback_isolated_page()`, `PageReported`, scatterlists, workqueues, RCU, static branches, module parameters, and zone watermarks.

Notable risks:
- The callback runs outside the zone lock, so the code must rotate freelists and restart safely after dropping the lock.
- Marking a page reported is valid only if it returns as the same buddy order; coalesced pages need reporting at the larger order later.
- Registration is singleton by design; concurrent users receive `-EBUSY`.
