# File Research: sources/os/plan9/9front/sys/src/cmd/spin/pangen1.c

`pangen1.c` is a large part of Spin’s `pan` verifier generator. It emits C header/source fragments for state-vector layout, process structures, queue structures, process creation, queue operations, global/local initialization, claim setup, reachability tables, state labels, variable dumping, and selected helper routines.

`genheader()` writes core verifier definitions: word size, sync/async counts, core count defaults, process-name/type arrays, process structure typedefs via `put_ptype()`, special never-claim wrapper structures for multiple claims, imported template fragments, the `State` structure, TRIX state support, and hidden-variable declarations. It depends heavily on template arrays from `pangen1.h`, `pangen3.h`, and `pangen6.h`.

`genaddproc()` emits the generated `addproc()` switch, process initialization cases through `put_pinit()`, predefined `np_` initialization, optional multiple-claim initialization, and `provided()` gating when proctypes use `provided` clauses. `put_pinit()` sets `_t`, `_p`, priority, reached-state bits, parameters, locals, embedded-code local initialization, and claim metadata.

Variable generation is split across `doglobal()`, `dolocal()`, `do_var()`, `do_init()`, and `typ2c()`. These functions order variables by type, generate struct fields, initialize scalars/arrays/channels, log ranges, warn about reducible types, reject local variables in never claims, and account for bitfield packing through `nBits`/`LstSet`. `walk_struct()` is declared for structured variable traversal and used when structs need initialization/logging.

Queue generation is handled by `genaddqueue()`. It emits queue type typedefs, `NQS`, field storage widths, queue-size helpers, TRIX sizing helpers, random receive-poll helper `Q_has()`, generated `qsend()`, queue-full/synchronous checks, generated receive field extraction and message removal, q-size switch code, prototypes, and the `Addproc` macro.

Other generator support includes `end_labs()` for stop/progress/accept/visible state tables, `c_chandump()`/`c_var()`/`c_wrapper()` for runtime variable and queue printing, `huntstart()`/`huntele()` for resolving executable elements through skips/gotos/unless, `qlen_type()` for compact queue-length fields, and small template emitters `ntimes()`/`ncases()`.

Important risks and coupling: this file assumes normalized `Element`/`Sequence` graphs from `flow.c`, queue metadata from `mesg.c`, process metadata from parser/analyzer state, and many global counters (`nrRdy`, `nqs`, `mst`, `Mpars`, `Npars`, `nclaims`). Generated C correctness depends on exact type widths, array bounds, state numbering, and template fragment compatibility.
