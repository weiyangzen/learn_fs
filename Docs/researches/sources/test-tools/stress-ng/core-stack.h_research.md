# sources/test-tools/stress-ng/core-stack.h

## Purpose
`core-stack.h` declares stack utility APIs used by stressors and signal-handling paths to reason about stack direction, alternate signal stacks, stack-top alignment, stack-smash checking, and backtraces.

## Important APIs, Types, And Functions
`STRESS_SIGSTKSZ` and `STRESS_MINSIGSTKSZ` resolve through runtime helpers rather than compile-time constants. `stress_align_stack` masks a stack-top pointer down to a 16-byte boundary. The exported API includes `stress_stack_direction`, `stress_stack_top`, `stress_stack_sigalt_no_check`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `stress_stack_sigstksz`, `stress_stack_minsigstksz`, `stress_stack_smash_check_flag_set`, and `stress_stack_backtrace`.

## Control Flow
Callers allocate or locate a stack region, compute the architecture-correct top with `stress_stack_top`, optionally align it, and install or disable an alternate signal stack. Stack-size macros defer to implementation code so platform-specific signal-stack sizes can be handled centrally.

## State And Persistence
The header itself stores no state. The implementation behind these declarations likely owns process-local signal-stack state and a stack-smash check flag. No persistent filesystem state is involved.

## Dependencies And Integration Points
It includes `stress-ng.h` for common attributes, types, and platform feature definitions. Integration points are signal stressors, alternate-stack tests, backtrace/debug paths, and any stressor that allocates stacks manually.

## Risks
Stack alignment and direction handling are architecture-sensitive; wrong assumptions can corrupt call frames or signal delivery. Alternate signal stack sizes vary across libc/kernel combinations, so compile-time constants are intentionally avoided. Backtrace behavior may be unavailable or unsafe in signal contexts depending on platform.

## Test Signals
Build coverage validates declarations across platforms. Runtime signals come from stack-oriented stressors, signal stressors using alternate stacks, and command-line cases such as `--stack`, `--stackmmap`, and backtrace-on-failure paths.
