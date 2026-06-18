<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s -->
# sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s

## Purpose
amd64 Go assembly trampoline for calling C functions embedded in `.syso` objects from Go.

## Important APIs, Types, And Functions
Defines `TEXT ·spacer(SB)` and `TEXT ·syso(SB),$0-16`; passes function pointer in `SI` and state pointer in `DI` before `CALL *SI`.

## Control Flow
The wrapper receives a C function pointer and state pointer from Go, moves them into x86-64 ABI argument registers, calls the C function, and returns.

## State And Persistence Behavior
No persistent state; it mutates registers and whatever memory the C function modifies.

## Dependencies And Integration Points
Used by `fibber` generated wrappers on linux/amd64. Must match Go assembler syntax and System V x86-64 ABI.

## Risks And Edge Cases
The comments acknowledge this is a fragile Go-to-C transition without cgo. Stack maps, preemption, and ABI drift are risks.

## Test Signals
Signals are successful Go build and correct calls to `fib_init`/`fib_next`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/go/fibber/fibs_linux_amd64.s -->
