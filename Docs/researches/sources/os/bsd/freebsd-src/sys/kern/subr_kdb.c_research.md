# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_kdb.c

## Purpose
Implements the machine-independent kernel debugger interface: backend selection, sysctl triggers, break-sequence handling, debugger entry/trap routing, backtraces, and thread enumeration helpers.

## Key Elements
- Global state: `kdb_active`, `kdb_dbbe`, `kdb_thread`, `kdb_frame`, `kdb_why`.
- Backend linker set: `kdb_dbbe_set`.
- Null backend: `KDB_BACKEND(null, ...)`.
- Sysctls under `debug.kdb`: available/current/enter/panic/panic_str/trap/trap_code/stack_overflow and break toggles.
- Entry points: `kdb_enter()`, `kdb_trap()`, `kdb_init()`.
- Break handling: `kdb_break()`, `kdb_alt_break()`, `kdb_alt_break_gdb()`.
- Backtraces: `kdb_backtrace()`, `kdb_backtrace_thread()`.
- Backend selection: `kdb_dbbe_select()`.
- Thread helpers: `kdb_thr_first()`, `kdb_thr_next()`, `kdb_thr_lookup()`, `kdb_thr_select()`, `kdb_thr_ctx()`.

## Behavior
`kdb_init()` initializes every backend, selects the highest-priority active backend, and reports available/current backends. Sysctls allow backend selection, debugger entry, deliberate panic, deliberate data/code faults, and stack overflow testing.

Break handling supports direct break-to-debugger and an alternate console sequence: carriage return, tilde, then control-B for debugger, control-P for panic, or control-R for reboot. The dcons-specific variant can force the gdb backend.

`kdb_trap()` disables interrupts, stops other CPUs when needed, marks the scheduler stopped, captures trapframe and PCB context, selects the current thread, grabs the console, invokes the selected backend trap method, supports backend switching, then restores CPUs and interrupt state.

## Research Notes
Debugger entry is gated by securelevel and MAC policy in `kdb_backend_permitted()`. Reentry uses a saved jump buffer so nested debugger faults can recover through `kdb_reenter()`.
