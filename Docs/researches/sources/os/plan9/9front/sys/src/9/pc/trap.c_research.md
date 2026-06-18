# File Research: sources/os/plan9/9front/sys/src/9/pc/trap.c

## Role

Core x86 trap, interrupt, page-fault, syscall, notification, and register-state handling for the PC kernel.

## Main Interfaces

- `trapinit0()` builds the early IDT before malloc is available.
- `trapinit()` installs special handlers after IRQ setup.
- `trap()` is the common trap/interrupt dispatcher except for direct syscall entry.
- `syscall()`, `notify()`, `noted()`, `execregs()`, `forkchild()`, and register helpers define user/kernel transition state.

## Key Behavior

- Initializes all 256 IDT entries from `vectortable`; breakpoint and syscall vectors are DPL 3.
- Dispatches hardware IRQs through `irqhandled()` before exception handling.
- User exceptions post debug notes using `usertrap()`.
- Kernel trap handling has special fixups for segment-register restore faults, `iret` faults, RDMSR/WRMSR faults, and `_peekinst`.
- `fault386()` handles page faults, including `vmapsync()` for kernel mappings and user fault-note delivery.
- Debug-register exceptions post watchpoint notes based on DR6/DR7 state.
- `notify()` builds the user notification frame; `noted()` restores or saves user state based on note action.
- `setregisters()` preserves privileged flags while allowing devproc-style register updates.

## Dependencies And Assumptions

- Depends on x86 vectors, segment selectors, low-level CR/DR/MSR helpers, Plan 9 process notes, and scheduler state.
- Assumes syscall enters directly from assembly and has already built a valid `Ureg`.
- Stack dumping uses kernel text-range heuristics and can be disabled with `*nodumpstack`.

## Research Notes

- The file contains both early-boot fatal trap support and mature user-process exception semantics.
- Kernel fault fixups are tightly coupled to assembly labels used by fork return, segment loads, MSR access, and safe probing.
