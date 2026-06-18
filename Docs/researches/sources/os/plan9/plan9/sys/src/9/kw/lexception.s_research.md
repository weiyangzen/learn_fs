# File Research: sources/os/plan9/plan9/sys/src/9/kw/lexception.s

## Role

ARM exception vector and trap-entry assembly for the Kirkwood kernel. It defines vector stubs, saves register state, switches stack modes, and calls C handlers for traps, syscalls, IRQs, and FIQs.

This is trap infrastructure, not filesystem code.

## Main Interfaces

- `vectors(SB)`: vector branch table.
- `vtable(SB)`: vector target table.
- Exception stubs:
  - `_vrst`
  - `_vsvc`
  - `_vund`
  - `_vpabt`
  - `_vdabt`
  - `_virq`
  - `_vfiq`
- `setr13(SB)`: sets mode-specific stack pointer.

## Important Behavior

- SWI/syscall entry saves user state, adjusts return PC, switches to supervisor mode, and calls `syscall`.
- Undefined instruction, prefetch abort, data abort, and IRQ paths build a `Ureg` frame and call `trap`.
- IRQ entry separately handles interrupt masking and stack switching.
- User exceptions restore user registers and resume via exception return semantics.
- FIQ path acknowledges with a minimal return sequence.

## Dependencies And Assumptions

- Includes `arm.s`.
- Assumes `Ureg` layout and PSR mode constants match `ureg.h`/`arm.h`.
- Calls C functions `syscall` and `trap`.

## Notable Risks

- Register save/restore layout must exactly match C `Ureg`.
- Any mismatch in mode-specific stack setup can corrupt kernel or user state.
