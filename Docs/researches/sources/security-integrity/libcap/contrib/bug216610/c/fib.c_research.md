<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/fib.c -->
# sources/security-integrity/libcap/contrib/bug216610/c/fib.c

## Purpose
C Fibonacci kernel used by bug216610 to demonstrate calling C object code from a pure-Go binary via `.syso` and assembly trampolines.

## Important APIs, Types, And Functions
Defines `struct state { uint32_t b, a; }`, `fib_init(struct state *)`, and `fib_next(struct state *)`.

## Control Flow
`fib_init` sets `a=0` and `b=1`. `fib_next` computes `next=a+b`, shifts `a=b`, and stores `b=next`.

## State And Persistence Behavior
Mutates only the caller-provided state struct.

## Dependencies And Integration Points
Compiled into target `.syso` files and called from Go `fibber.State` through generated linkname wrappers.

## Risks And Edge Cases
The C struct layout must match the Go `State` layout and assembly calling convention exactly. `uint32_t` Fibonacci values overflow naturally.

## Test Signals
Signals are expected first Fibonacci sequence values printed by `go/main.go`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/c/fib.c -->
