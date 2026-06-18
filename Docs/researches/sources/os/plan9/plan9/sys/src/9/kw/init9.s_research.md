# File Research: sources/os/plan9/plan9/sys/src/9/kw/init9.s

## Role

Small ARM assembly startup wrapper for the user-level boot program. It sets the static base register and calls `startboot`.

This is boot/bootstrap glue, not filesystem code.

## Main Interface

- `TEXT main(SB), 1, $8`

## Important Behavior

- Loads `setR12(SB)` into `R12` to establish the Plan 9 static base.
- Places `boot(SB)` and an argument vector pointer on the stack.
- Calls `startboot(SB)`.
- Loops forever if `startboot` returns.

## Dependencies And Assumptions

- Assumes ARM Plan 9 calling conventions.
- Assumes `boot` and `startboot` symbols are linked into the boot image.

## Notable Risks

- Minimal bootstrap code with no error path; returning from `startboot` hangs.
