# File Research: sources/os/plan9/plan9/sys/src/9/ppc/trap.c

PowerPC trap, interrupt, syscall, fault, note, and process register handling.

Key responsibilities:
- Manages interrupt handler registration through `intrenable`/`intrdisable`.
- Decodes PPC exception causes and dispatches external interrupts, decrementer clocks, data/instruction faults, TLB misses, syscalls, FP unavailable traps, and program exceptions.
- Implements lazy FP restore/init and FP state gating in trap/syscall return.
- Bridges PPC faults to common `fault()` through `faultpower`.
- Writes exception vectors with `sethvec` and miss vectors with `setmvec`.
- Dispatches interrupt vectors from board-specific `intvec`, calls registered handlers, acknowledges through `intend`, tracks timing/count statistics, and preempts.
- Provides stack/register dump helpers, `callwithureg`, `dumpstack`, and `dumpregs`.
- Sets up kernel process children, validates alignment, handles `execregs`, `forkchild`, `userpc`, `setregisters`, `setkernur`, and `dbgpc`.
- Implements full syscall dispatch and Plan 9 note delivery/return (`notify`, `noted`).

Important behavior:
- User trap entry records kernel-entry cycles and saves `up->dbgreg`.
- Syscalls take syscall number from `r3`; arguments are copied from user stack `Sargs`.
- `NOTED` is handled specially before normal notify.
- `notify` saves `Ureg` on the user stack and disables active FP state.
- Interrupt dispatch loops up to 64 vectors per external interrupt.

Dependencies:
- Must match `l.s` `Ureg` layout and exception frame conventions.
- Depends on board-specific `vectorenable`, `vectordisable`, `intvec`, `intend`.
- Uses port `systab`, notes, process, fault, and tracing infrastructure.

Notable risks:
- Contains diagnostic FP state checks that can print/dump/panic on inconsistencies.
- Vector patching emits raw instruction words and must stay ISA-encoding-correct.
- `if(vno > nelem(vctl))` should conceptually be `>=`; vector 256 would index out of range.
