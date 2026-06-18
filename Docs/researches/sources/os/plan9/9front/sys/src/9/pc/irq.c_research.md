# File Research: sources/os/plan9/9front/sys/src/9/pc/irq.c

## Purpose
Implements architecture-neutral interrupt/trap handler registration and dispatch for the PC kernel.

## Key Elements
Maintains `vctl[256]` handler chains, `vclock` for the clock handler, and interrupt service-time histograms. `irqhandled()` dispatches traps and interrupts, performs ISR/EOI callbacks, updates per-Mach interrupt accounting, calls registered handlers, handles clock preemption, and logs or probes spurious interrupts. `trapenable()` registers CPU exception handlers below `VectorPIC`. `intrenable()` maps IRQs through architecture hooks, chains compatible handlers, enables hardware delivery, and records the clock handler. `intrdisable()` removes matching handlers and disables hardware delivery when appropriate. `irqinit()` exposes an `irqalloc` arch file listing vector, IRQ, and handler name.

## Dependencies
Depends on `Vctl`, `arch->intrirqno`, `arch->intrassign`, `arch->intrvecno`, optional `arch->intrspurious`, memory allocation, locks, `trap`, `preempted`, and arch-file registration.

## Behavior/Risks
Shared interrupt chains require compatible ISR/EOI semantics. On multiprocessor systems, removed `Vctl` objects may be delayed through a small ring before free to reduce races with in-flight dispatch.
