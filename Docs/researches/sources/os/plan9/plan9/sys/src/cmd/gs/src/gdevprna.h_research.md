# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprna.h

This header documents and declares the asynchronous printer support implemented in `gdevprna.c`.

The long design comment is the most important content. It explains that async drivers create two instances of the same printer device: a writer instance used by the interpreter to build command lists, and a renderer instance used by a separate thread to rasterize queued command-list pages. The normal path queues complete pages, while low-memory situations can queue partial pages so the renderer can free command-list memory and let interpretation continue.

The header documents the memory-safety model: the writer reserves enough band-list memory to queue partial pages, while the renderer runs in a fixed memory space. To make this practical, the writer restricts command-list content by avoiding complex paths, pre-clipping output unless the clip path is simple, and limiting high-level images. This is described as a "restricted bandlist format."

The opening protocol requires concrete drivers to call `gdev_prn_async_write_open` instead of `gdev_prn_open`, after installing required callbacks such as `start_render_thread`, `buffer_page`, and `print_page_copies`, and setting band sizing parameters. The render thread must call `gdev_prn_async_render_thread` with the start-render parameter block.

`gdev_prn_start_render_params_s` carries the writer device pointer, an open semaphore for synchronization, and the renderer open status. `init_async_render_procs` is a convenience macro for installing the driver callbacks required by the async layer.

The declared public functions are:

- `gdev_prn_async_write_open(...)`
- `gdev_prn_async_render_open(...)`
- `gdev_prn_async_render_thread(...)`

Filesystem relevance: indirect through command-list/band-list file management. The header is primarily concurrency, memory, and printer-driver architecture documentation.
