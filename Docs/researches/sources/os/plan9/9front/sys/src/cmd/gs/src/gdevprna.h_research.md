# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprna.h

Public header and design notes for Ghostscript asynchronous printer rendering.

Key contents:
- Explains the async model: a writer instance records command lists during interpretation, while a renderer instance consumes completed or partial page command lists in another thread/context.
- Documents partial-page behavior under memory pressure and the use of reserve bandlist memory to avoid deadlocks.
- Describes driver obligations for async open: initialize render-thread, buffer-page, print-page-copies, space parameters, and optional parameter/hardware/render open hooks before calling `gdev_prn_async_write_open`.
- Describes renderer synchronization: driver `start_render_thread` must start or rendezvous with a renderer that calls `gdev_prn_async_render_thread`, then signals open status.
- Defines `gdev_prn_start_render_params`, carrying the writer device pointer, open semaphore, and renderer open status.
- Provides `init_async_render_procs` macro to install async render-thread, buffer-page, and print-page-copies callbacks.
- Declares `gdev_prn_async_write_open`, `gdev_prn_async_render_open`, and `gdev_prn_async_render_thread`.

Notable dependencies:
- Generic printer support from `gdevprn.h`.
- Semaphore abstraction from `gxsync.h`.

Research notes:
- This header is unusually documentation-heavy and is the best guide for concrete async printer driver integration.
- The spelling/wording reflects old comments, but the operational contract is clear: async drivers must call these helpers instead of normal `gdev_prn_open` on the writer/renderer paths.
