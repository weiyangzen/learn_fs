# File Research: sources/os/plan9/plan9/sys/src/9/ppc/init9.s

## Role

Tiny PPC assembly entry wrapper equivalent to calling `startboot(argv0, &argv0)`.

## Control Flow

`_main` sets the static base register `R2` with `setSB(SB)`, allocates a small frame, stores incoming `argv0` from `R3` on the stack, passes its address as the second argument, branches to `startboot`, then loops forever if it returns.

## Dependencies

Uses Plan 9 PPC assembler syntax and ABI assumptions: `R3` holds first argument, `R2` is SB, and `startboot` is available.

## Risks

This exists specifically to avoid C runtime dependencies before SB setup. Stack offsets are ABI-sensitive.
