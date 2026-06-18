## sources/security-integrity/libcap/goapps/captrace/captrace.go

Purpose: user-facing tracing tool that uses `bpftrace` kprobes/kretprobes on `cap_capable` to report kernel capability checks for all processes, a PID, or a launched command.

Important APIs/types/functions: flags `--bpftrace`, `--debug`, `--pid`; `thread` struct stores PPID, datum, capability value, and command token; global mutex-protected `tids` and `cache`; functions `event()`, `tailTrace()`, `tracer()`, and `main()`.

Control flow: starts `bpftrace` with probes emitting `CB` begin and `CE` end lines, scans stdout, caches begin events by tid, matches returns to log capability result and errno detail, filters to a PID tree when requested or when launching a command, and kills/waits the tracer after a launched command.

State/persistence: runtime maps of tracked PIDs and in-flight events; launches external processes; no files.

Dependencies/integration: `bpftrace`, kernel BPF/kprobe permissions, Go cap names for formatting, `/proc` process identity through bpftrace `pid/tid/comm`.

Risks: requires high privilege and kernel tracing support; begin/end matching by tid can race or be overwritten under concurrent nested checks; parser depends on exact printed space-separated format.

Test signals: run against a command that needs a known capability, verify successful and failing checks, run `--pid` filter, and validate cleanup of bpftrace child.
