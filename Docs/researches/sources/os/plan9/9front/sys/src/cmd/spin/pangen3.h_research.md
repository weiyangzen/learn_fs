# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen3.h

Large generated-runtime template for verifier data structures, process/channel allocation, queue operations, prototypes, and compile-option reporting.

Key template groups:
- `Head0`, `Header`, `Header0`, and `Head1`: define verifier types and compile-mode setup, including `Trans`, `State`, `_Stack`, `Svtack`, `H_el`, `Trail`, BFS trail/state records, TRIX pointer access, vector sizing, fairness fields, and reduction/storage flags.
- `Addp0`/`Addp1`: generated `addproc` body skeleton for process allocation, state-vector growth, offset/skip management, TRIX allocation, fairness bounds, VECTORSZ checks, and initial process field setup.
- `Addq0`/`Addq1` and `Addq11` through `Addq5`: generated queue creation, send, rendezvous checks, xr/xs channel checks, length/full tests, receive extraction, and collapse compression hooks.
- `R0`/`R00`/`R0a`/`R2`/`R3`/`R4`/`R5`/`R6`/`R7a`/`R7b`/`R8a`/`R8b`: snippets for per-process/per-queue initialization, reachability checks, collapse compression, TRIX re-marking, and BFS_PAR mask/offset preservation.
- `R12` through `R15`: queue field receive and undo templates.
- `Proto`: generated function prototypes and core hash/trail/state declarations.
- `SvMap`: generated `to_compile` reporter that reconstructs compile-time `cc -D...` flags.

Key behavior:
- Defines verifier storage layout and the Trail frame fields used by forward/backward move code.
- Provides generated queue semantics including sorted send support, rendezvous channel checks, receive removal/shifting, and event-trace hooks.
- Provides xr/xs assertion enforcement for partial-order reduction soundness.
- Provides collapse-mode process/channel compression templates and BFS_PAR copy-on-mask/offset helpers.
- Records compile configuration for reproducibility.

Dependencies:
- Filled in by generator routines in `pangen2.c`, `pangen4.c`, and related files based on process and queue tables.
- Assumes generated process structs `P*`, queue structs `Q*`, global arrays, and macros from `pan.h`.

Research notes:
- This header is one of the core generated verifier runtime templates.
- Process/channel layout, undo code, collapse compression, and BFS_PAR behavior are tightly coupled; altering one fragment requires checking all generated modes.
