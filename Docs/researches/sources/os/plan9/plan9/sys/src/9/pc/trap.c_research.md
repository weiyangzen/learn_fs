# File Research: sources/os/plan9/plan9/sys/src/9/pc/trap.c

Purpose: Core x86 PC trap, interrupt, syscall, note, and process-register handling for the Plan 9 kernel.

Main structures/globals:
- `vctl[256]`: vector table of registered trap/interrupt handlers.
- `vctllock`: protects handler registration/removal.
- `intrtimes[256][Ntimevec]`: histogram of interrupt service times.
- External/implicit core structures: `Ureg`, `Mach`, `Proc`, `Tos`, `Vctl`.

Key logic:
- `trapinit0` builds the IDT very early, before malloc, installing interrupt gates for all vectors and giving user privilege to breakpoint and syscall vectors.
- `trapinit` registers special handlers for breakpoint, page fault, double fault, and unexpected vector 15; enables NMI; exposes `irqalloc`.
- `intrenable` creates a `Vctl`, asks `arch->intrenable` for a vector, chains compatible handlers on shared vectors, and records ISR/EOI callbacks.
- `intrdisable` removes a registered interrupt handler and disables the hardware IRQ when no handlers remain.
- `trapenable` registers non-IRQ trap handlers below `VectorPIC`.
- `trap` is the central dispatcher: handles registered vectors, calls ISR/handler/EOI, accounts interrupt time, posts notes for user exceptions, fans out unknown interrupts to all registered IRQ handlers as a spurious fallback, and panics on kernel traps.
- `fault386` handles page faults using CR2, delegates VM sync for kernel vmaps, calls `fault`, and posts debug notes or panics.
- `syscall` validates syscall entry from user mode, handles tracing, copies user args, dispatches `systab`, stores return value/error state, processes `noted`, notes, and delayed scheduling.
- `notify` builds the user-space note frame and redirects execution to the process notify handler.
- `noted` validates and restores a user-provided `Ureg` after note handling, with `NCONT`, `NRSTR`, `NSAVE`, `NDFLT`, and invalid-argument behavior.
- Helpers include `dumpregs`, stack dumping, `validalign`, `execregs`, `userpc`, `setregisters`, `kprocchild`, `forkchild`, `setkernur`, and `dbgpc`.

Dependencies and integration:
- Tightly integrated with x86 architecture hooks (`arch->intrenable`, IDT vectors, CR registers), Plan 9 scheduler/proc/note/syscall systems, page fault machinery, and `devarch` file exposure.
- Includes generated syscall tables from `../port/systab.h`.

Risks and notes:
- Interrupt sharing depends on matching ISR/EOI callbacks for chained handlers.
- Unknown interrupt fallback calls every registered interrupt routine, which can help shared/spurious cases but may be costly or surprising.
- User note restoration carefully preserves protected flags/segments, but invalid user frames lead to process suicide.
- Several panic paths intentionally dump registers/stack for kernel faults.
