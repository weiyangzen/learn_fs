# File Research: sources/os/plan9/plan9/sys/src/9/kw/fpiarm.c

## Role

ARM floating-point instruction emulator for the Kirkwood port. It decodes old ARM FPA-style floating-point instructions, emulates arithmetic through Plan 9's portable floating-point package, and also handles a few special atomic instruction encodings.

This is CPU trap support, not filesystem code.

## Main Interfaces

- `fpiarm(Ureg *ur)`: emulates consecutive FP/special instructions starting at the trapped PC.
- Special instruction helpers:
  - `casemu`
  - `ldrex`
  - `strex`
  - `clrex`
- Internal FP operation helpers:
  - binary: `fadd`, `fsub`, `fsubr`, `fmul`, `fdiv`, `fdivr`
  - unary: `fmov`, `fmovn`, `fabsf`, `frnd`
  - load/store: `fld`, `fst`
  - compare: `fcmp`

## Important Behavior

- Uses `FPsave` in the current `Proc` as the emulated FPU register state.
- Initializes FP state lazily when a process first executes an FP instruction.
- Decodes conditional execution with `condok`.
- Supports FPA load/store, register transfers, compare operations, and arithmetic operations.
- Unsupported FP instructions call `unimp`, which raises a Plan 9 error.
- `casemu` validates user memory and emulates a compare-and-swap-like operation.
- `ldrex`/`strex` use a global `ldrexvalid` flag, which models only a very coarse exclusive monitor.

## Dependencies And Assumptions

- Uses `../port/fpi.h` for the portable internal FP representation.
- Uses `Ureg` layout offsets to read and write general registers.
- Assumes `up` is non-nil and points to the current process.
- Relies on `validaddr`, `splhi`, and `spllo` for safe memory access and atomicity.

## Notable Risks

- Does not fully model ARM FP trap status or all FP exception semantics.
- Exclusive monitor emulation is global and simplified.
- Unsupported instruction paths raise process errors rather than providing complete architecture coverage.
