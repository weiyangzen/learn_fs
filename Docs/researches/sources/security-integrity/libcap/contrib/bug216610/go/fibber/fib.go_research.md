<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go

## Purpose
Go wrapper package for the bug216610 Fibonacci C kernel.

## Important APIs, Types, And Functions
Defines `State { B, A uint32 }`, method `cPtr`, constructor `NewState`, and method `Next`.

## Control Flow
`NewState` allocates `State` and calls generated `syso__fib_init.call`. `Next` calls generated `syso__fib_next.call` to advance the state.

## State And Persistence Behavior
State lives in the Go heap but is mutated by C object code through unsafe pointers.

## Dependencies And Integration Points
Depends on generated `linkage.go`, target assembly `syso` trampoline, and `.syso` symbols from `fib.c`.

## Risks And Edge Cases
Unsafe pointer conversion assumes `State` layout matches C `struct state`. Generated symbol wrappers must exist before build.

## Test Signals
Signals are correct Fibonacci sequence values from the main program.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fib.go -->
