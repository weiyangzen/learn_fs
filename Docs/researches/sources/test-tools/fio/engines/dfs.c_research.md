# sources/test-tools/fio/engines/dfs.c

Purpose: Implements the DAOS File System (`dfs`) fio engine using DAOS pool/container handles, DFS objects, and asynchronous DAOS event queues.

Important APIs/functions: Registers `dfs` with setup/init/prep/cleanup, file open/close/stat/unlink/invalidate, queue/getevents/event, and per-IO init/free. Global helpers initialize and clean DAOS/DFS connections. Queue operations call `dfs_write()`, `dfs_read()`, and DAOS event APIs.

Control flow: Per-thread init allocates `daos_data`, creates an IO pointer array sized to `iodepth`, and under a mutex initializes global DAOS state on first use: `daos_init`, pool connect, container open, DFS mount, and optional object class lookup. It then creates a per-thread event queue and increments thread count. File open maps fio create/read/write options to DFS flags and opens a DFS object. Queue builds a one-element scatter/gather list, initializes a DAOS event, issues async read/write, increments queued count, and returns queued. `getevents()` polls the DAOS event queue until `min` completions, transfers errors/resid to `io_u`, finalizes events, and returns completed `io_u`s through `event()`. Cleanup destroys the event queue, frees per-thread data, and closes global DAOS state when the last thread exits.

State/persistence: Global pool/container/DFS handles and object class are shared across threads; per-thread state includes event queue, one open object pointer, queued count, and completion array. Per-IO `daos_iou` holds event and SGL state.

Dependencies/integration: Requires DAOS/DFS libraries and version-specific APIs. Integrates with fio diskless/nodiskutil behavior and file lifecycle callbacks.

Risks: Only init/cleanup are mutex-protected; shared global handles are used concurrently. `daos_data` stores a single `dfs_obj_t *`, so multiple files per job may overwrite object state. Some error paths after `daos_event_init()` do not finalize the event. Poll loop ignores timeout argument and can spin with sleeps only through DAOS nowait polling.

Test signals: DAOS integration tests should cover missing options, version-specific UUID/label paths, multi-thread init/cleanup, multiple files, read/write completion errors, unlink, and iodepth saturation.
