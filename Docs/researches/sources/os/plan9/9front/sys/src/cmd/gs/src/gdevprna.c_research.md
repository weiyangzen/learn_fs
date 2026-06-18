# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.c

Generic asynchronous printer support for Ghostscript. It creates a writer device that records command lists and a renderer device running in another thread or rendezvous context, connected by a page queue and shared band-list allocator.

Key behavior:
- `gdev_prn_async_write_open` allocates fixed-size renderer memory, allocates locked bandlist memory, forces banding and read-only space parameters, copies the writer device to create the renderer instance, opens the writer as a command-list device, initializes a shared page queue, starts the renderer thread through the driver-supplied hook, waits on an open semaphore, and installs a memory-recovery callback.
- Writer-side proc reinitialization installs async close/output/put-params/get-hardware-params handlers and a bandlist-memory recovery hook.
- `gdev_prn_async_write_close_device` queues a terminate action, waits for the renderer to drain, closes the writer, and frees async allocations.
- `gdev_prn_dealloc` frees the copied renderer device, renderer allocator, page queue, and locked bandlist allocator.
- `gdev_prn_async_render_open` opens the renderer side with `is_async_renderer` set; `gdev_prn_async_render_close_device` closes it through normal printer close.
- `gdev_prn_async_render_thread` opens the renderer, signals open status, loops over queued full/partial/copy page entries, installs queued `page_info`, runs clist setup, calls output-page behavior according to queue action, finalizes queue entries, and shuts down on terminate.
- `gdev_prn_async_write_put_params` cascades to the original put-params without closing, flushes/reallocates when geometry or space parameters changed, or emits parameter changes into the command list when no reallocation is needed.
- `gdev_prn_async_write_get_hardware_params` waits for the page queue to empty before querying the renderer's hardware parameters.
- `gdev_prn_async_render_put_params` applies clist-supplied params on the renderer and tries to reopen if the device closed itself.
- `gdev_prn_async_write_output_page` ends the writer clist page, enqueues a full or copy page, finishes the writer page when appropriate, and reopens new band files, waiting for rendered pages if memory is tight.
- `gdev_prn_async_write_free_up_bandlist_memory`, `flush_page`, and `reopen_clist_after_flush` support partial-page flushing and VM-error recovery.
- `alloc_bandlist_memory` builds a monitor-locked allocator over either a malloc allocator or a debug fixed-size allocator.
- `alloc_render_memory` creates a fixed-limit non-GC renderer allocator chunk and disables normal GC reclamation for it; paired free helpers tear these allocators down.

Notable dependencies:
- Async printer API from `gdevprna.h`.
- Ghostscript allocator, device, memory-locking/retry, no-GC, clist, page queue, path, and halftone-cache internals: `gsalloc.h`, `gsmemlok.h`, `gsmemret.h`, `gsnogc.h`, `gxcldev.h`, `gxclpath.h`, `gxpageq.h`, `gzht.h`.

Research notes:
- The async implementation relies on concrete drivers supplying `start_render_thread`, and optionally render open/close and buffering behavior.
- Comments emphasize deadlock avoidance under low memory: writer reserves bandlist resources and renderer uses a bounded allocator.
- Some error handling is intentionally weak: renderer output errors are mostly ignored because the loop has no clear recovery path.
- `reopen_clist_after_flush` is defined but not used in this file.
