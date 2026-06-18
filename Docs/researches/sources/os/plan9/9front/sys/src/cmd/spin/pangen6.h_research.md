# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen6.h

## Purpose

`pangen6.h` is a generated-code template, not a conventional C header. It defines two string arrays used by Spin's code generator:

- `Code2e[]`: platform-specific atomic test-and-set and compare-and-swap support emitted for multicore and parallel BFS builds.
- `Code2c[]`: the large multicore verifier runtime fragment emitted into generated `pan.c` when `NCORE > 1`.

The generated code supports multicore depth-first verification with shared memory, per-core work queues, optional global queues, crash and termination detection, optional disk overflow, full error trails, and separate POSIX and Windows implementations.

## Atomic Primitives

`Code2e[]` emits `tas()` implementations for x86/x86_64, ARM, SPARC, Itanium, and PowerPC64, with a compile-time error for unsupported platforms. It also emits `cas()` as GCC `__sync_bool_compare_and_swap` unless `NO_CAS` is set, in which case it falls back to a `tas()`-guarded software compare-and-swap.

The generated fragments are guarded by multicore/parallel BFS and non-Windows preprocessor conditions; Windows-specific atomic support appears later in `Code2c[]` through `InterlockedBitTestAndSet`.

## Core Runtime Structures

`Code2c[]` emits:

- work-queue frame sizing macros such as `GN_FRAMES`, `LN_FRAMES`, `VMAX`, `PMAX`, `QMAX`, and `OFFT`;
- shared-memory sizing variables such as `SEG_SIZE`, `LWQ_SIZE`, and `GWQ_SIZE`;
- timeout/crash detection parameters `ONESECOND`, `SHORT_T`, `LONG_T`, `Delay`, and `OneHour`;
- `SM_frame`, the state handoff frame that stores a state vector, mask, process/channel offset tables, `tau`, `o_pm`, rendezvous metadata, and optional full-trail/C-state stack data;
- `sh_Allocater`, a shared-state-memory pool descriptor with POSIX and Windows variants;
- `SM_results`, a statistics/reachability payload passed around at shutdown.

It also emits global variables for worker/proxy process IDs, shared memory IDs, queue pointers, shared locks, queue counters, crash heartbeat arrays, stats counters, and trail-root bookkeeping.

## Multicore Statistics and Shutdown

`record_info()` copies local counters and `reached` arrays into an `SM_results` frame. `retrieve_info()` merges another worker's results into the local aggregate. `sleep_report()` prints lock wait and queue wait statistics and may suggest larger queues or different compile-time flags. `check_overkill()` recommends a smaller `VMAX` when observed handoff state vectors were much smaller than the compile-time maximum.

`sudden_stop()` initiates abnormal termination, marks `search_terminated`, optionally removes shared memory segments, kills or interrupts workers/proxy processes, and calls `wrapup()` from core 0 when possible. `someone_crashed()` watches neighbor heartbeats and termination flags to detect crashed workers.

## Shared Memory and Queues

The POSIX branch emits `init_shm()`, `prep_shmid_S()`, `prep_state_mem()`, `init_HT()`, and `cleanup_shm()` using `ftok`, `shmget`, `shmat`, `shmdt`, and `shmctl`. It can allocate a shared bitstate/hash arena, separate state memory, or linked shared allocation pools. It supports `SEP_STATE`, `SEP_HEAP`, `BITSTATE`, `COLLAPSE`, `MEMLIM`, and Cygwin segment-size constraints.

The Windows branch emits equivalents using `CreateFileMapping`, `OpenFileMapping`, `MapViewOfFile`, `UnmapViewOfFile`, and `CloseHandle`, plus Windows process creation for worker and proxy processes.

Queue operations include:

- `Get_Full_Frame()` waits for a populated local frame and opportunistically consumes from the global queue;
- `Get_Free_Frame()` waits for an empty local or global slot;
- `GlobalQ_HasRoom()` reserves and fills a global queue slot when the local target queue is full;
- `Read_Queue()` drives worker-side consumption, termination query forwarding, `QUIT`/statistics aggregation, and successor exploration through `new_state()`.

Termination detection is token/query based: the root initiates `QUERY`, workers forward either `QUERY` or `QUERY_F`, and the root sends `QUIT` when all queues remain empty and no global queue changes occurred.

## State Handoff and Reconstruction

`mem_put()` serializes the current state into an `SM_frame`, including `now`, compression masks, process/channel offsets, optional C stack data, full-trail stack pointers, handoff count, `tau`, `o_pm`, `boq`, and vector size. `unpack_state()` reverses that process, restores `now`, `Mask`, offsets/skips, C tracked state, trail metadata, accepting/progress markers, and root/trail bookkeeping.

`mem_hand_off()` decides whether to hand off a DFS state when depth exceeds `z_handoff`, subject to safety/liveness, rendezvous, verification, and atomic-move constraints. `mem_put_acc()` provides a liveness-mode handoff path. `write_root()` and `set_root()` persist and restore a root `SM_frame` for partial trail reconstruction, including per-core `cpuN_rst` suffix fallback.

When `FULL_TRAIL` is enabled, the emitted `Stack_Tree` support records a shared linked trail stack with `Push_Stack_Tree()`, `Pop_Stack_Tree()`, and cached shared allocation.

## Disk Overflow

Under `USE_DISK`, the template emits temporary queue spill files (`QNNN_CCC.tmp`) and helpers:

- `mem_file()` writes serialized `SM_frame` records to disk when memory queues are full;
- `mem_drain()` moves disk-backed frames back into a target queue when room appears;
- `dsk_stats()` reports and removes temporary files.

## Platform Differences

The POSIX path uses `fork()` to create workers and optional proxy send/receive halves, then marks shared segments for removal early with `IPC_RMID` when possible. The Windows path builds `pan.exe`/`pan_proxy.exe` command lines and uses `CreateProcess`. Both paths converge on the same conceptual queue, state handoff, stats, and termination logic.

## Notable Risks and Behaviors

- Many fields are marked `volatile` because frames and queues are shared across processes.
- Frame availability is signaled by `m_vsize`; writers set it last and readers clear it after use.
- Queue counters are often read outside locks as optimistic hints, then rechecked under locks where needed.
- The generated code has many compile-time modes with incompatible combinations explicitly rejected, such as `BFS` with `NCORE` and `MA` without `SEP_STATE`.
- This header is source text embedded in C string arrays; escaping and conditional fragments are part of the generator interface.
