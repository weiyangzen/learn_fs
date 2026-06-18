<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Makefile -->
# sources/security-integrity/libcap/contrib/bug216610/Makefile

## Purpose
Build orchestration for bug216610, a Go internal-linker/.syso experiment combining Go, assembly trampolines, and C object code.

## Important APIs, Types, And Functions
Targets include `go/fib`, generated `go/fibber/fib_$(GOTARGET).syso`, `go/fibber/linkage.go`, `Dockerfile`, `arms`, and `clean`. Uses `GOTARGET` from `go env`.

## Control Flow
Native build compiles `c/fib.c` through `c/gcc.sh` into a `.syso`, generates Go linkname wrappers with `package_fns.sh`, then builds the Go program with `CGO_ENABLED=0`. `arms` builds cross `.syso` files inside Docker.

## State And Persistence Behavior
Creates `.syso`, generated `linkage.go`, the `go/fib` binary, Dockerfile, and optional arm artifacts; clean removes them.

## Dependencies And Integration Points
Depends on Go, GCC, objdump, assembly files named by host target, Docker for cross builds, and the libcap `psx` module imported by the Go program.

## Risks And Edge Cases
The build relies on target-specific assembly trampolines and generated linknames. Missing `fibs_$(GOTARGET).s` or cross compiler support breaks the build.

## Test Signals
Signals are successful `go build`, generated linkage for exported C functions, and working Fibonacci output.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/bug216610/Makefile -->
