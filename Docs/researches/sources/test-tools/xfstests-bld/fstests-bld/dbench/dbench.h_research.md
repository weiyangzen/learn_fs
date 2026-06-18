<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h -->
# sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h

Source read: complete file, 190 lines, 3938 bytes, sha256 `bb109ca6217103f6653741050952ba8325bb7135c1fcd103074d19860706494e`. Final split target: `Docs/researches/sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h_research.md`.

Purpose: central public header for the bundled dbench/tbench sources. It gathers portability includes from `config.h`, defines shared constants, declares benchmark state structs, imports generated prototypes from `proto.h`, and exposes the global `options` instance.

Important APIs/types/functions: `struct op` records per-operation counts, total time, and max latency; `struct child_struct` carries per-client identity, status flags, byte counters, rate state, per-operation statistics, benchmark directory, and a backend-private pointer; `struct options` holds command-line/build-time behavior such as process count, sync behavior, fsync policy, TCP options, warmup/timelimit, target rate, xattr enablement, fake I/O, cleanup, and reporting flags. It also defines SMB-style create disposition and create option constants used by trace replay functions.

Control flow: this file has no executable control flow. Its inclusion order is important: system headers and fallback macros are established before `proto.h`, so generated prototypes can refer to `struct child_struct`, `struct options`, `BOOL`, `uint32`, and `uint32_t`.

State and persistence behavior: no state is persisted by the header itself. It defines the in-memory contract used by child processes and declares `extern struct options options`, whose concrete storage is supplied by program modules such as `tbench_srv.c` or the dbench main program.

Dependencies and integration: depends on autoconf feature macros for headers, xattr APIs, `MSG_WAITALL`, and `O_DIRECTORY`. It integrates the direct file backend (`fileio.c`), socket backend (`sockio.c`), socket helpers, xattr wrappers, utility functions, and generated prototypes into one compile-time interface.

Risks: `uint32` is an old unsigned-int alias that can hide width assumptions; `O_DIRECTORY` fallback is Linux-specific octal; duplicate `nb_*` prototypes in `proto.h` assume mutually exclusive link targets for file and socket backends. Any change to shared structs has cross-file ABI impact inside the benchmark.

Test signals: successful compilation across configured platforms is the main signal. Trace replay tests should exercise both dbench and tbench builds because they select different `nb_*` implementations behind the same header contract.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/dbench/dbench.h -->
