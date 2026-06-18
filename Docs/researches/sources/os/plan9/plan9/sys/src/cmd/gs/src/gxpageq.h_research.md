# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxpageq.h

`gxpageq.h` declares Ghostscript's page queue interface for coordinating interpreter-produced command-list pages with renderer threads. It depends on `gsmemory.h`, `gxband.h`, and `gxsync.h`.

The central type is `gx_page_queue_action_t`, which encodes `PARTIAL_PAGE`, `FULL_PAGE`, `COPY_PAGE`, and `TERMINATE`. The long header comment is the key contract: page descriptions may be split into partial entries, copied pages must preserve rendered state for PostScript `copypage`, full pages complete or cancel page sequences, and terminate entries end rendering after prior required output.

The file forward-declares `gx_page_queue_t` and defines `gx_page_queue_entry_t`, which stores `gx_band_page_info_t page_info`, action, copy count, and queue/next links. `private_st_gx_page_queue_entry()` supplies GC metadata for `next` and `queue`.

Public operations allocate queues and entries, initialize/destroy queues, free page-info resources separately from entry objects, enqueue pages, add pages using a reserve entry under memory pressure, block until one/all pages finish rendering, and dequeue/finish entries. The implementation lives elsewhere, but this header defines the threading and ownership protocol. A notable risk is that callers must explicitly call `gx_page_queue_entry_free_page_info` before freeing entries unless `gx_page_queue_finish_dequeue` is used; otherwise command-list memory leaks.
