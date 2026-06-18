# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen1.h

## Purpose

`pangen1.h` is not a conventional declaration header. It contains large static arrays of C string literals used by `pangen1.c` to generate Spin’s verifier source. The main arrays are:

- `Code2a[]`: startup/runtime support, trail replay, BFS support, bitstate setup, and related verifier scaffolding.
- `Code2d[]`: timers, main search routines, DFS/BFS dispatch, hashing, error handling, trail writing, compression, state storage, option parsing, and memory management.

The generated output becomes part of `pan.c` and related verifier code.

## Major Generated Components

### `Code2a[]`

`Code2a` emits the tail of generated `run()` and several runtime helpers:

- State table printing and dot-output exit path.
- BFS/TRIX allocation before global initialization.
- `iniglobals(...)` and initial never-claim/process startup.
- Partial-order reduction stutter-invariance warning.
- Bitstate hash-array initialization and repeated hash runs.
- Stack/state-vector allocation.
- `Printf` and `cpu_printf` wrappers.
- Disk-backed stack frame retrieval under `SC`.
- `pan_exit`.
- C-code trail text transmogrification for embedded `{c_code...}` references.
- Source/trail replay helpers:
  - `wrap_trail`
  - `findtrail`
  - `getrail`
- Trail file creation through `make_trail`.
- Bitstate storage variants:
  - `bstore_mod`
  - `bstore_reg`
- TRIX restore/repopulate support.
- BFS data structures and logic:
  - `SV_Hold`
  - `EV_Hold`
  - `BFS_Trail`
  - `getsv`
  - `getsv_mask`
  - `push_bfs`
  - `pop_bfs`
  - `store_state`
  - `bfs`
  - `putter`
  - `nuerror`

### `Code2d[]`

`Code2d` emits most of the generated verifier runtime:

- Timing and snapshot functions:
  - `start_timer`
  - `stop_timer`
  - `snap_time`
  - `snapshot`
- Multi-core crash detection:
  - `crash_reset`
  - `crash_test`
  - optional alert reporting.
- Search entry point:
  - `do_the_search`
- Generated transition dispatch:
  - `do_transit`
  - `do_reverse`
  - includes generated `FORWARD_MOVES` and `REVERSE_MOVES`.
- Event trace handling:
  - `require`
- Predicate support:
  - `enabled`
- Main DFS engine:
  - `new_state`
- Assertions and bounds:
  - `spin_assert`
  - `Boundcheck`
- Statistics and shutdown:
  - `wrap_stats`
  - `wrapup`
  - `stopped`
- Hashing:
  - optional SuperFastHash.
  - Jenkins 32-bit or 64-bit hash.
  - `d_hash`
  - `s_hash`
  - mask setup.
- Main program option parsing:
  - `main`
  - `usage`
- Memory allocation:
  - `Malloc`
  - `emalloc`
- Fatal and recoverable error handling:
  - `Uerror`
  - `uerror`
- Trail writing:
  - `puttrail`
  - multi-core reverse trail support.
- State-vector save/restore:
  - `sv_save`
  - `sv_restor`
  - `p_restor`
  - `q_restor`
- Dynamic process/channel removal:
  - `delproc`
  - `delq`
- End-state and cycle checks:
  - `qs_empty`
  - `endstate`
  - `checkcycles`
- Stack matching:
  - `onstack_init`
  - `grab_state`
  - `onstack_put`
  - `onstack_now`
  - `onstack_zap`
- Hashtable initialization:
  - `hinit`
- Compression/state storage:
  - collapse compression via `ordinal` and `compress`
  - default compression
  - hash compact support
  - MA graph encoding via `gstore`
  - TRIX `sv_populate`
  - main `hstore`
- Final inclusion of generated transition tables through `#include TRANSITIONS`.

## Search Semantics Encoded

The generated DFS/BFS logic supports many Spin verification modes:

- Safety checking.
- Acceptance cycle detection.
- Non-progress cycle detection.
- Weak fairness.
- Partial-order reduction.
- Rendezvous behavior.
- Atomic and `d_step` sequencing.
- Timeout/stuttering behavior.
- Never claims and multi-claim selection.
- Event trace and negated trace checking.
- Bounded context switching.
- Randomized process or transition ordering.
- Bitstate/supertrace approximation.
- Full-stack and counter-stack matching.
- Hash compaction and collapse compression.
- Multi-core state handoff.
- TRIX tree index compression.
- Breadth-first search with optional disk spill.

## Compile-Time Coupling

This template is governed by dense preprocessor combinations, including:

`BFS`, `TRIX`, `BITSTATE`, `FULLSTACK`, `CNTRSTACK`, `SAFETY`, `VERI`, `NOREDUCE`, `NOFAIR`, `NP`, `NCORE`, `SEP_STATE`, `HAS_CODE`, `HAS_UNLESS`, `HAS_PROVIDED`, `EVENT_TRACE`, `COLLAPSE`, `HC`, `MA`, `BCS`, `REACH`, `SVDUMP`, `MEMLIM`, `SC`, `RANDSTOR`, `P_RAND`, and `T_RAND`.

Many incompatible combinations are rejected in generated `main` with `#error`, runtime warnings, or option validation.

## Filesystem and Storage Behavior

Although this is not filesystem implementation code, generated verifier code performs several file operations:

- Trail creation and replay:
  - `.trail`, `cpuN_trail`, and custom suffix trail files.
  - Read-only trail mode with `-T`.
  - Exclusive trail creation with `-x`.
- Stack spill under `SC`:
  - `stack2disk`
  - `disk2stack`
  - configurable stack file.
- BFS disk spill:
  - temporary `pan_bfs_<n>.tmp` files.
- State-vector dump:
  - `<PanSource>.svd`.
- MA checkpoint hooks:
  - `R_XPT`
  - `W_XPT`.

These are verifier artifact operations, not Plan 9 filesystem behavior.

## Risks and Maintenance Notes

This file is highly sensitive generated-code infrastructure. The search algorithm is encoded as strings, so normal C compiler checking applies only after generation. Template syntax, escaping, and `%` formatting must remain exactly aligned with `pangen1.c`’s `fprintf` and `ntimes` usage.

The generated code uses fixed-size buffers, raw `sprintf`/`strcpy`/`strcat`, and many global variables. Most inputs are controlled by Spin’s own generated names and command-line options, but the style is legacy and fragile.

`new_state` is intentionally macro-heavy and difficult to read. The file itself recommends preprocessing generated `pan.c` for a chosen mode before studying or modifying the search routine.

Any change here should be verified by generating and compiling `pan.c` across representative modes: plain DFS, `-DSAFETY`, `-DBITSTATE`, `-DBFS`, `-DNOREDUCE`, `-DNP`, `-DTRIX`, multi-claim verification, and models with rendezvous channels.
