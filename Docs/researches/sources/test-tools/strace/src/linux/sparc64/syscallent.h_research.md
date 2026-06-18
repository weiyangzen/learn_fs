# sources/test-tools/strace/src/linux/sparc64/syscallent.h

## Purpose
Defines the SPARC64 primary syscall dispatch table consumed by `syscall.c` through the `syscallent.h` include path. The entries map numeric syscall IDs to argument counts, strace classification flags, decoder symbols via `SEN(...)`, and displayed syscall names. This table is SPARC-specific rather than a generic 64-bit table because SPARC keeps historical numbering, sparc32 holes, SPARC-only calls, socket subcalls, and IPC placement.

## Important APIs, Types, and Functions
The file contributes initializer rows for `struct_sysent` arrays built in `syscall.c`. It uses strace table macros such as `SEN`, flags like `TD`, `TF`, `TP`, `TS`, `TCL`, `TM`, `TI`, `NF`, `PU`, and decoder names including `clock_sparc64_adjtime`, `adjtimex64`, `rt_sigtimedwait_time64`, `futex_time64`, and `printargs`. It defines `SYS_socket_subcall 500` before including `../64/subcallent.h`, which aligns socket subcall decoding for SPARC64.

## Control Flow and Integration
There is no runtime control flow in this header; compile-time inclusion creates the syscall table. `syscall.c` indexes the resulting table by `tcp->scno` after architecture-specific syscall-number extraction. The table includes `syscallent-common.h` after a reserved SPARC range and includes 64-bit subcalls after setting the socket subcall base. Comments mark sparc32-only slots and reserved gaps so the primary 64-bit personality does not accidentally decode 32-bit-only syscalls.

## State and Persistence
The file stores no mutable state. Its persistent effect is the compiled static syscall metadata used for tracing, filtering, seccomp BPF generation, counting, and syscall name lookup.

## Dependencies
Depends on the surrounding strace syscall table machinery: `syscall.c` table inclusion, decoder declarations, flag macros, SPARC common entries, and `../64/subcallent.h`. Several decoder names depend on architecture-specific time/stat/IPCs support elsewhere in the source tree.

## Risks
Wrong numbers or flags cause silent mis-decoding, incorrect filtering, or wrong argument formatting for SPARC64. Time-related rows are sensitive because SPARC64 uses 64-bit time decoders for many historical syscall numbers. The socket subcall base must remain coordinated with `../64/subcallent.h`. Gaps documented as sparc32-only or reserved should not be filled without confirming kernel ABI numbering.

## Test Signals
Useful signals include successful compile of the SPARC64 table, syscall name lookup tests around holes and high-number common syscalls, SPARC64 traces for `clock_adjtime`, `adjtimex`, IPC calls at 392-402, and socket subcalls beginning at 500. Generated table sanity checks should verify no entry exceeds `MAX_ARGS` and that common includes land after the intended reserved range.
