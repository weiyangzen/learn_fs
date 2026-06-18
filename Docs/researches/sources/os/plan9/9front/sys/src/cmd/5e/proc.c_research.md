# File Research: sources/os/plan9/9front/sys/src/cmd/5e/proc.c

This file manages emulator process state, executable loading, stack initialization, fd-table state, errors, and Plan 9 note delivery.

Process setup:
- Defines packed `Tos`, matching Plan 9 top-of-stack layout enough to populate pid/profiling fields.
- `initproc()` allocates current `Process`, sets pid, fd table, process list, and resets FPA/VFP state.
- `addproc()`, `remproc()`, and `findproc()` maintain the global process list under `plistlock`.
- `copyname()` updates process display name and shared executable path reference.

Stack and executable loading:
- `initstack()` builds initial ARM user stack with argc, argv pointers, strings, top-of-stack pointer in R0, clock pointer in R1, and SP in R13.
- `inittos()` writes pid into emulated `Tos`.
- `loadscript()` handles `#!` scripts by parsing interpreter and reinvoking `loadtext()`.
- `loadtext()` opens and validates an ARM executable, resets process memory/register/note state, creates text/data/BSS/stack segments, reads file contents, sets PC to entry, clears OCEXEC fds, initializes stack, and resets FP state.

Fd table:
- `newfd()`, `copyfd()`, `fddecref()`, `iscexec()`, `setcexec()`, and `fdclear()` manage a refcounted bitmap of close-on-exec file descriptors.

Errors and notes:
- `cherrstr()` sets per-process error string.
- `noteerr()` records host error text on failed syscalls.
- `addnote()` queues host notes into the emulated process note ring.
- `donote()` builds a user-register frame and note string on the emulated stack, jumps to the emulated notify handler, runs until `noted()`, then restores registers depending on noted action.

Dependencies and interactions:
- Uses `mach` executable headers, memory helpers from `seg.c`, syscall note constants, and FPA/VFP reset functions.
- Used by `5e.c`, `sys.c`, and `fs.c`.

Research relevance:
- This is the emulator’s process and exec model.

Risk notes:
- `loadscript()` tokenizes the shebang line in-place and has simple whitespace parsing.
- `donote()` runs nested `step()` calls under `setjmp`/`longjmp`, so state restoration is delicate.
- Segment copies during `rfork()` are implemented in `sys.c`, while base segment allocation lives here/`seg.c`.
