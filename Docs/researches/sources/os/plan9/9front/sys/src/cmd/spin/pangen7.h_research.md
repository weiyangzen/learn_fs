# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen7.h

## Purpose

`pangen7.h` is another generated-code template. Its `pan_par[]` string array emits `pan.p`, the parallel BFS verifier runtime for generated Spin verifiers compiled with `BFS_PAR`. It implements shared-memory parallel breadth-first exploration, optional fixed-size queues, optional FIFO behavior, optional disk-backed queues, error-trail support, shared allocation, locking, statistics, and shutdown handling.

The emitted runtime is POSIX-oriented: it uses System V shared memory, `fork`, `usleep`, `nanosleep`-adjacent includes, and optional `.spin` disk directories.

## Shared BFS Runtime Model

The generated structures are:

- `BFS_Slot`, a queue cell containing optional FIFO message type and a `BFS_State *`.
- `BFS_data`, per-core statistics copied back into shared memory.
- `BFS_shared`, the shared root object containing quit/start flags, lock arrays, optional owner/check arrays, per-core stats/flags/idle bits, queue heads/tails or fixed queue arrays, memory allocator state, and optional disk/logging fields.

`BFS_GEN` creates two generations for normal non-FIFO breadth-first operation: one generation is being consumed while successors are placed into the other. `bfs_toggle` selects the active generation. `BFS_QSZ` switches queue storage to fixed-size arrays and disables recycling/disk/FIFO combinations that are incompatible.

## Setup and Main Loop

`bfs_main()` validates unsupported cycle detection, chooses a core count, optionally creates `.spin` disk queues, calls `bfs_setup()`, runs the search, collects statistics, reports timing, drops shared memory, and exits.

`bfs_setup_mem()` finds the largest available shared memory segment with `bfs_find_largest()`, attaches it as `BFS_shared`, and initializes the shared allocator. `bfs_setup()` forks worker processes and divides most shared heap memory into per-core local heaps with a reserve. `bfs_run()` pushes the initial state from core 0, waits for all cores, then repeatedly consumes slots from `bfs_next()`, explores states, recycles slots, detects idle/empty generations, toggles BFS generations, and eventually sets `quit`.

`bfs_next()` scans incoming queues and returns either a real state slot or `bfs_null`. It supports FIFO queue sweeping, fixed-size queue arrays, disk-backed source reads, staggered output flushing, and idle-bit updates.

## State Packing and Exploration

`bfs_pack_state()` serializes the current state, trail metadata, rendezvous state, masks/offsets, proviso metadata, and optional verbose counters into a `BFS_Slot`. It uses shared memory holders (`SV_Hold`, `EV_Hold`) to store state vectors and masks. `bfs_new_sv()` and `bfs_new_sv_mask()` reuse immutable or freed vector/mask holders to reduce shared-memory churn.

`bfs_unpack_state()` restores `now`, `vsize`, `Mask`, process/channel offsets, trail metadata, C tracked state, rendezvous/atomic/preselection markers, depth, and Q-proviso tags from a queue slot. It also returns old state vectors to local free lists.

`bfs_explore_state()` is the generated BFS successor loop. It unpacks the slot, handles depth limits, optional separate hash checking, verification claim scheduling, partial-order preselection, rendezvous retry/failure, atomic sequences, timeouts, unless escapes, event traces, C-state restoration, transition execution/reversal, and successor storage. Successors are queued through `bfs_store_state()`.

`bfs_store_state()` handles duplicate detection with `b_store`, `o_store`, or `h_store`, separate hashing (`BFS_SEP_HASH`), claim-move intermediate state handling, Q-proviso tags, rendezvous-complete marking, and `bfs_push_state()` for new or intermediate states.

## Queues, Disk, and Memory

`bfs_push_state()` chooses a destination core randomly unless `BFS_GREEDY`, `BFS_STAGGER`, or `BFS_SEP_HASH` pins the target. It supports fixed-size queue overflow accounting, FIFO tail insertion, linked-list head insertion, and disk sinking.

When `BFS_DISK` is set, queue payloads are written to `.spin/q<generation>_<dst>_<src>` files. Helpers include `bfs_disk_start()`, `bfs_disk_stop()`, `bfs_disk_inp()`, `bfs_disk_out()`, close helpers, `bfs_sink_disk()`, and `bfs_source_disk()`.

Memory allocation is split between `sh_pre_malloc()` for pre-run shared allocation and `sh_malloc()` for per-core local heaps with shared reserve fallback. `bfs_get_shared_mem()` attaches the main segment and `bfs_drop_shared_memory()` detaches/removes it. `bfs_find_largest()` probes System V shared memory in 32 MB increments up to word-size or `MEMLIM` limits and emits sysctl hints when only the default 32 MB segment is available.

## Locking, Crash Handling, and Statistics

`e_critical()` and `x_critical()` wrap shared locks using generated `tas()`, with optional `BFS_CHECK` owner/count validation and lock override if the holder's `bfs_flag` shows abnormal termination. `bfs_clear_locks()` clears locks owned by the current process during shutdown. `bfs_all_running()`, `bfs_all_idle()`, `bfs_idle_and_empty()`, `bfs_mark_done()`, and `bfs_set_toggle()` implement termination and crash coordination.

`bfs_snapshot()` prints per-core progress and updates shared per-core statistics. `bfs_statistics()` merges results, calls `wrapup()` on core 0, and reports lock wait counts. `bfs_update()` collects child core stats and `reached` arrays; `bfs_putreached()`, `bfs_getreached()`, and `bfs_offset()` manage per-core reachability snapshots stored in shared memory.

## Error Trails

The template emits BFS-specific trail writers:

- `bfs_write_snap()` writes trail fragments robustly;
- `bfs_one_step()` records one transition ID;
- `bfs_putter()` recursively writes parent trail frames;
- `bfs_nuerror()` creates an error trail with verification/merged headers;
- `bfs_uerror()` reports non-fatal errors and decides whether to write trails or shut down;
- `bfs_Uerror()` reports fatal BFS runtime errors and shuts down.

`BFS_NOTRAIL` and `BFS_DISK` enable trail-frame recycling through `bfs_grab_trail()` and `bfs_release_trail()`.

## Notable Risks and Behaviors

- The generated runtime is heavily controlled by compile-time feature macros. Some combinations are explicitly rejected (`MA`, `BCS`, `BFS_FIFO` with `BFS_DISK`, `BFS_QSZ` with FIFO/disk).
- Non-FIFO mode is generation-based and does not require strict FIFO order; FIFO mode keeps deleted markers and sweeps queues.
- If shared memory runs out, the runtime may punt states as a last resort before shutting down, depending on the path.
- The state exploration loop shares much logic with the normal verifier engine but adapts it to queued BFS frames instead of recursive DFS stack frames.
- This file is C code embedded as strings; downstream correctness depends on generator emission order and macro compatibility.
