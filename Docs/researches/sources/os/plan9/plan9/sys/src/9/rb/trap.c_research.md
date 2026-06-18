# File Research: sources/os/plan9/plan9/sys/src/9/rb/trap.c

RouterBoard MIPS trap, interrupt, syscall, register dump, and note-delivery implementation.

Key responsibilities:
- Dispatches MIPS exception codes to interrupt handling, VM faults, kmap faults, VCE diagnostics, watchpoints, FPU emulation, user notes, or kernel panic/exit.
- Maintains interrupt handler chains per interrupt level, enables RouterBoard APB UART subinterrupts, masks jabbering interrupts, and periodically resets interrupt counts.
- Handles clock interrupts, device interrupt polling, preemption, and delayed scheduling at trap exit.
- Implements Plan 9 user notification (`notify`, `noted`, `validstatus`) and the MIPS user-stack frame used for note handlers.
- Implements system call entry directly from assembly, including syscall tracing, argument validation, error-stack handling, `NOTED` special handling, note delivery, and return-value placement.
- Provides process fork/kproc register setup (`forkchild`, `kprocchild`), exec register setup (`execregs`), user PC helpers, and kernel stack/register dump helpers.

Important behavior:
- Kernel KSEG3 TLB faults are routed to `kfault`; user TLB faults are passed to `faultmips`.
- Floating-point coprocessor unusable traps from user mode are handled by software FP emulation because the port has no usable FPU path here.
- `#define setstatus(v)` makes the status updates in this file no-ops as an experiment noted in the source.
- Interrupt `pollall` treats `ILduart0` specially through APB subinterrupt status.

Dependencies and assumptions:
- Trap-frame offsets must match `mem.h`, `ureg.h`, and assembly vector code.
- Depends on `faultmips`, `fpuemu`, `fpwatch`, scheduler, note, syscall, and Plan 9 port-layer process APIs.

Notable risks:
- Note return validation preserves interrupt mask and forbids privileged/user-hostile status bits, but any trap-frame ABI mismatch would corrupt user return.
- Jabber suppression disables interrupt sources after 25,000 handler invocations within a reset interval.
- Kernel exceptions generally dump registers/stack and call `exit(1)` rather than trying to recover.
