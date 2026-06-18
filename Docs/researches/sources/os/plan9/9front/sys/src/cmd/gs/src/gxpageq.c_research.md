# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.c

Ghostscript page queue implementation for coordinating queued band/page rendering work.

Key behavior:
- Defines `gx_page_queue_s`, containing allocator, monitor, queue count, dequeue-in-progress flag, render request/done semaphores, FIFO entry links, and a reserve entry.
- Allocates queue objects and queue entries using Ghostscript memory descriptors.
- `gx_page_queue_init` creates the monitor, semaphores, and reserve entry; `gx_page_queue_dnit` drains queued entries, closes page info resources, and frees synchronization objects/reserve entry.
- Low-level add/remove helpers maintain FIFO ordering under the monitor.
- `gx_page_queue_wait_one_page` and `gx_page_queue_wait_until_empty` let producers wait until pending or in-progress rendering completes.
- `gx_page_queue_enqueue` adds an entry and signals the render request semaphore.
- `gx_page_queue_add_page` allocates or consumes the reserve entry, fills action/page info/copy count, enqueues it, then waits as needed until a new reserve entry can be allocated.
- `gx_page_queue_start_dequeue` waits for render requests, marks dequeue in progress, and removes the first entry.
- `gx_page_queue_finish_dequeue` optionally signals render completion, clears dequeue-in-progress, closes clist page resources, frees the entry, and exits the monitor.

Notable dependencies:
- Page queue declarations from `gxpageq.h`.
- Band/page info and clist cleanup from `gxclist.h`.
- Ghostscript monitor/semaphore primitives via device infrastructure.

Research notes:
- The reserve-entry design provides a fallback path when entry allocation fails, ensuring a page can still be queued before waiting for memory to become available.
- `gx_page_queue_add_page` documents that an entry may have been queued even if it later returns an error while trying to restore the reserve entry.
