## sources/security-integrity/libcap/go/mismatch.go

Purpose: negative psx test that should fail/panic because `gettid` returns different values across threads and therefore violates psx all-thread consistency expectations.

Important APIs/functions: `psx.Syscall3(syscall.SYS_GETTID, ...)`.

Control flow: calls the all-thread syscall wrapper for `GETTID` and prints the returned tid/error; Makefile expects this command to fail.

State/persistence: no persistent state.

Dependencies/integration: Go psx package and Go runtime threads. Used by `go/Makefile` as an expected-failure test.

Risks: if psx consistency detection regresses, this may incorrectly succeed; output is diagnostic rather than structured.

Test signals: `./mismatch || exit 0 ; exit 1` in `make -C go test`, plus cgo variant when applicable.
