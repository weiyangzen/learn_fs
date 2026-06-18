# sources/test-tools/syzkaller/vm/vmimpl/openbsd.go

Purpose: helper for retrieving OpenBSD DDB diagnostics after a panic or hang.

Important APIs/types/functions: `DiagnoseOpenBSD(w io.Writer)`.

Control flow: writes debugger commands to disable pagination/wrapping, show panic, trace, registers, process lists, locks, malloc/pools, and traces for CPU 0 and CPU 1. It sleeps one second after each command and returns `nil, true` to ask the caller to wait for console output.

State and persistence: no durable state; command text is sent to the provided console writer.

Dependencies and integration: depends only on `io` and `time`. The OpenBSD `vmm` backend calls it from `Diagnose`.

Risks: typo in comment aside, functionality assumes the console is at DDB; if not, commands may have side effects in a shell. Fixed sleeps slow triage.

Test signals: no direct unit test. Indirect coverage comes from OpenBSD VM crash integration.
