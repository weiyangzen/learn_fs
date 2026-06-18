<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/main.go -->
# sources/security-integrity/libcap/contrib/bug216610/go/main.go

## Purpose
Demo program for bug216610. It proves psx syscall use and the `.syso` Fibonacci bridge work in a pure-Go binary.

## Important APIs, Types, And Functions
Uses `psx.Syscall3(syscall.SYS_GETPID)`, `fibber.NewState`, and `State.Next`.

## Control Flow
Gets PID through psx, prints it, initializes Fibonacci state, prints the first two values, advances eight times, and prints the sequence prefix.

## State And Persistence Behavior
No persistent state; process output is the observable result.

## Dependencies And Integration Points
Imports local module `fib/fibber` and libcap `psx` package. Built by the bug216610 makefile.

## Risks And Edge Cases
Fails if psx syscall wrapper or generated syso bridge is unavailable. Fibonacci values are fixed-width uint32.

## Test Signals
Signals are printed PID and Fibonacci sequence `0, 1, 1, 2, 3, 5, ...`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/main.go -->
