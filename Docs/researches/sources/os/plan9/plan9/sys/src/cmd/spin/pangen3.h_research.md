# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen3.h

This header contains embedded generated-verifier source fragments for `pan.h` and runtime support around state-vector layout, process/channel allocation, send/receive helpers, assertions, prototypes, and compile-option reporting.

Key contents:
- `Head0[]`, `Header[]`, `Header0[]`, and `Head1[]`: generated `Trans`, stack-frame, saved-vector, and `State` declarations plus compile-mode normalization.
- `Addp0[]`/`Addp1[]`: generated `addproc()` body for allocating process slots in the state vector or TRIX structures.
- `Addq0[]`/`Addq1[]`: generated `addqueue()` body for queue allocation.
- `Addq11[]` through `Addq5[]`: generated queue send, receive, length, fullness, rendezvous, `xr`/`xs`, and collapse-compression helpers.
- `Code0[]`, `Code1[]`, `Code3[]`, `R0[]`, `R0a[]`, `R2[]`, `R3[]`, `R4[]`, `R5[]`, `R6[]`, `R8a[]`, `R8b[]`, `R12[]`: generated initialization and per-process/per-queue setup fragments.
- `R13[]`, `R14[]`, and `R15[]`: generated queue undo helpers `unsend()` and `unrecv()`.
- `Proto[]`: generated prototypes and optional global arrays for `xr`/`xs`.
- `SvMap[]`: generated `to_compile()` function that prints the compile flags used for `pan.c`.

Important details:
- State-vector offsets are kept in `proc_offset[]` and `q_offset[]` unless `TRIX` is used.
- `addproc()` aligns process frames, updates `vsize`, masks padding for compression, initializes `_pid`, and enforces `MAXPROC`/fairness limits.
- `addqueue()` similarly aligns queue frames and initializes queue type metadata.
- Queue operations validate uninitialized/deleted channels, support TRIX backup pointers, event-trace hooks, rendezvous checks, sorted send, random receive, and field count handling.
- `q_S_check()` and `q_R_check()` enforce exclusive sender/receiver claims used by partial-order reduction.
- Collapse compression emits `col_p()` and `col_q()` to pack unmasked process/queue bytes and omit unused queue slots.
- `SvMap[]` preserves compile flags such as `BITSTATE`, `BFS`, `SAFETY`, `NOREDUCE`, `NP`, `COLLAPSE`, `MA`, `TRIX`, `NCORE`, `VECTORSZ`, and memory limits.

Filesystem relevance:
- Indirect. Generated code uses low-level `write()` in optional state-vector dump paths and reports compile commands, but the content is verifier runtime support.
