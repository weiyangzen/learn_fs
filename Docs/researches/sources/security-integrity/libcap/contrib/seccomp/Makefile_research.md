<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/Makefile -->
# sources/security-integrity/libcap/contrib/seccomp/Makefile

## Purpose
Makefile for the seccomp exploration program demonstrating interactions between no-new-privs, seccomp TSYNC, Go threads, and psx.

## Important APIs, Types, And Functions
Targets `all`, `go.sum`, `explore`, `test`, `sudotest`, and `clean`.

## Control Flow
Builds `explore.go`, tidies modules when `go.sum` is missing, and `sudotest` runs expected-success and expected-failure command variants with and without `--psx`.

## State And Persistence Behavior
Creates `explore` and `go.sum`; clean removes them.

## Dependencies And Integration Points
Depends on Go and sudo. Integrates with libcap `psx` module.

## Risks And Edge Cases
`sudotest` intentionally runs privileged seccomp experiments and expects some invocations to fail. The syscall number is x86_64-specific in the Go code.

## Test Signals
Signals are successful no-kill errno=0 runs and expected errors for default errno-blocking runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/Makefile -->
