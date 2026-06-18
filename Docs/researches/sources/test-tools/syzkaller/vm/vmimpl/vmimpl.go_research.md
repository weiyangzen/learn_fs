# sources/test-tools/syzkaller/vm/vmimpl/vmimpl.go

Purpose: defines the low-level VM backend interface and shared process/output lifecycle machinery used by all syzkaller VM implementations.

Important APIs/types/functions: `Pool`, `Instance`, `Infoer`, `Env`, `BootError`, `MakeBootError`, `InfraError`, `Register`, `Type`, global `Shutdown`, `ErrTimeout`, `ErrPreempted`, `Types`, `CmdCloser`, `MultiplexConfig`, `Multiplex`, `waitAndKill`, `RandomPort`, `UnusedTCPPort`, and `EscapeDoubleQuotes`.

Control flow: backends register a `Type` with constructor and capability flags. `Multiplex` starts a goroutine that waits for context timeout, instance close signal, or merger error. On stream error it waits briefly for the command, maps configured preemption errors, optionally sleeps for extra console output, closes controlled console readers, waits for the merger, and signals one final error. On timeout/close it kills the process and closes readers. Error types attach boot/infra output for higher-level reporting.

State and persistence: global backend registry and process-wide shutdown channel are persistent process state. Runtime state includes child processes, merger goroutines, channels, and optional console closers.

Dependencies and integration: central contract for all `vm/*` backends and the high-level `vm` package. Uses OS process control, random, networking, target timeouts, logging, and report types.

Risks: `Types` map is unsynchronized and assumes init-time registration; process killing is blunt; `CmdCloser.Close` assumes `Process` is non-nil; `Shutdown` cannot be reset; port allocation races are unavoidable.

Test signals: `vm_test.go`, `vm_full_test.go`, and `merger_test.go` cover key monitor/multiplex/merger paths. Backend integration tests cover interface compliance.
