# sources/test-tools/fio/engines/glusterfs_async.c

Purpose: Implements the experimental asynchronous GlusterFS gfapi fio engine `gfapi_async`.

Important APIs/functions: Defines per-IO `fio_gf_iou`, async callback `gf_async_cb()`, `fio_gf_async_queue()`, polling `fio_gf_getevents()`, `fio_gf_event()`, per-IO init/free, and setup wrapping the shared gfapi setup.

Control flow: Setup logs that async is experimental, initializes common gfapi state, forces thread mode, and allocates an `aio_events` array sized by iodepth. Queue submits gfapi async read/write, optional discard, fdatasync, or fsync operations with `io_u` as callback data. The callback marks `io_complete`. `getevents()` scans fio's in-flight IO list until enough completed flags are found, clears each flag, and stores completed `io_u`s in `aio_events`.

State/persistence: Each `io_u` has `fio_gf_iou` state with a completion flag. Per-thread `gf_data` stores completion array and shared file/glfs state.

Dependencies/integration: Depends on gfapi async APIs, shared `gfapi.h` helpers, fio in-flight IO list, and optional trim/new API compile flags.

Risks: Completion flag is not atomic or locked between callback and polling thread. Callback ignores return status, so IO errors are not propagated. `getevents()` busy-waits with `usleep(100)` and ignores timeout. The engine is explicitly marked experimental.

Test signals: Integration tests should cover read/write/sync completions, callback error propagation gaps, iodepth behavior, timeout behavior, and thread-safety under high concurrency.
