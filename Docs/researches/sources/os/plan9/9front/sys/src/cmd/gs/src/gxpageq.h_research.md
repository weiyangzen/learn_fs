# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxpageq.h

Ghostscript page queue interface for producer/renderer coordination around band-list pages. It declares the queue entry type, action enum, memory descriptors, and public lifecycle/synchronization routines used by the page writer and renderer threads.

Key contents:
- `gx_page_queue_action_t` defines `PARTIAL_PAGE`, `FULL_PAGE`, `COPY_PAGE`, and `TERMINATE` actions, with detailed ordering semantics for partial band-list fragments, `copypage`, `showpage`, cancelled pages, and shutdown.
- `gx_page_queue_entry_s` stores `gx_band_page_info_t`, action, copy count, FIFO link, and back-pointer to its queue.
- Queue APIs cover allocation, initialization/destruction, enqueue/add-page, blocking dequeue, finish-dequeue cleanup, and waiting for one or all queued pages to finish rendering.
- The comments explicitly separate freeing a queue entry from freeing its large page/band-list resources.

Notable dependencies:
- `gsmemory.h` for Ghostscript allocation.
- `gxband.h` for band-list page metadata.
- `gxsync.h` for monitor/thread synchronization primitives used by the implementation.

Research notes:
- This header is concurrency-facing but implementation details are intentionally hidden in `gxpageq.c`.
- The action comments are the most important contract: a renderer must preserve preceding partial and copy-page state until the corresponding full/copy page semantics are satisfied.
- There is a spelling typo in the comment/prototype area (`Declaraions`, `deqeueue`), but the API contract is clear.
