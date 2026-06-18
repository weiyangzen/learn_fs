# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/bpt.c

## Scope

Breakpoint management for `5i`.

## Behavior

- Lists instruction, read, write, access, and equality breakpoints with symbolized addresses.
- Adds breakpoints from debugger command text, defaulting to instruction breakpoints.
- Deletes breakpoints by evaluated address.
- `brkchk()` tests address/type matches, handles countdowns, and stops execution by setting `count = 1` and `atbpt = 1`.

## Dependencies

Uses command expression parsing, memory access for equality breakpoints, and shared global breakpoint list from `arm.h`.

## Risks And Invariants

- `delbpt()` increments `membpt` for deleted non-instruction breakpoints; this looks like it should decrement, so memory-breakpoint checks may remain enabled.
- Breakpoints are address exact-match only; no range or symbolic lifetime tracking.
