# sources/test-tools/syzkaller/vm/vmimpl/freebsd.go

Purpose: helper for collecting additional diagnostics from a panicked FreeBSD kernel through an interactive debugger console.

Important APIs/types/functions: `DiagnoseFreeBSD(w io.Writer)`.

Control flow: writes a blank line, disables debugger pagination and line wrapping, then sends `show registers`, `show proc`, `ps`, lock, malloc, UMA, and TCP control-block commands, sleeping one second between commands. It returns `nil, true`, meaning diagnostic output is expected to arrive asynchronously on the console stream.

State and persistence: no durable state; it only writes debugger commands to the provided writer.

Dependencies and integration: depends on an `io.Writer` connected to a FreeBSD DDB prompt. VM backends can call it from `Instance.Diagnose` when the parsed report suggests a FreeBSD panic.

Risks: if the console is not at DDB, commands may be typed into a login shell or lost; fixed sleeps make diagnosis slow; returned output is not captured directly.

Test signals: no direct unit test is assigned. Integration requires a FreeBSD VM panic path.
