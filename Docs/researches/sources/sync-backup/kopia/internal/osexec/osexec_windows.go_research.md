# sources/sync-backup/kopia/internal/osexec/osexec_windows.go

Purpose: Windows implementation of interrupt-signal isolation for child commands.

Important APIs/types/functions: `DisableInterruptSignal(c *exec.Cmd)`.

Control flow: sets Windows process creation flags so the child does not receive console Ctrl-C events as part of the parent process group.

State and persistence behavior: mutates `exec.Cmd.SysProcAttr` before process start; no persistence.

Dependencies and integration points: used by command-running code on Windows.

Risks and test signals: behavior depends on Windows console semantics. Tests should run a child command and verify parent interrupt handling separately from child lifetime.
