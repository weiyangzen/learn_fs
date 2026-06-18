# File Research: sources/os/plan9/plan9/sys/src/9/kw/trap.c

## Role

Kirkwood ARM trap, fault, and interrupt controller handling. It routes hardware IRQs, initializes high-vector exception tables, handles page faults, invokes FP emulation for undefined instructions, and provides debugging dump helpers.

This is core kernel exception infrastructure, not filesystem code.

## Main Interfaces

- Interrupt management:
  - `intrenable`
  - `intrdisable`
  - `intrclear`
  - `intrmask`
  - `intrunmask`
  - `intrhi`
  - `intrbridge`
  - `intrfmtcounts`
- Trap/fault:
  - `trapinit`
  - `trap`
  - `faultarm`
  - `writetomem`
- Debug/utility:
  - `dumpregs`
  - `dumpstack`
  - `callwithureg`
  - `probeaddr`
  - `idlehands`

## Data Structures

- `Handler`: installed handler entry with function, arg, name, and counter.
- `Irq`: per-interrupt handler table with mask/cause register pointers.
- `Vctl`: local interrupt control structure.

## Important Behavior

- Supports low, high, and bridge interrupt groups.
- `trapinit` masks interrupts, copies vector code to high vectors, sets up stacks, and initializes interrupt tables.
- `intrs` scans pending interrupt bits and calls installed handlers.
- Fault handling distinguishes user/kernel faults and read/write status.
- Page faults call Plan 9 `fault`; unresolved kernel faults panic.
- Undefined instructions are first offered to `fpiarm` for emulation.
- `probeaddr` safely tests whether a physical/virtual address can be read.

## Dependencies And Assumptions

- Uses Kirkwood interrupt register layout from `io.h`.
- Uses ARM fault status/address register helpers from `l.s`.
- Calls VM fault handling and Plan 9 note delivery.

## Notable Risks

- Shared interrupt handler tables are fixed-size.
- Fault recursion/stuck fault detection is heuristic.
- Interrupt masking and clear semantics must match Kirkwood hardware exactly.
