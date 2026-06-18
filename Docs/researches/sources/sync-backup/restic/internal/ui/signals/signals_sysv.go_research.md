# sources/sync-backup/restic/internal/ui/signals/signals_sysv.go

Purpose: SysV-like Unix implementation of progress signal registration.

Important APIs/types/functions: unexported `setupSignals()` calls `signal.Notify(signals.ch, syscall.SIGUSR1)`.

Control flow: selected on `aix`, `linux`, and `solaris`. Unlike BSD, it registers only `SIGUSR1`, because these platforms do not have portable `SIGINFO`.

State and persistence: process-local signal subscription only.

Dependencies/integration: pairs with the global channel from `signals.go`; consumers should not call this directly.

Risks: use of `SIGUSR1` may conflict with embedding applications or wrappers that also rely on that signal. The single global channel still means one consumer receives each signal.

Test signals: no direct tests; validated mainly by successful platform builds and runtime use of progress refresh.
