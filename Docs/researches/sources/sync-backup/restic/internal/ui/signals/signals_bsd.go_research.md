# sources/sync-backup/restic/internal/ui/signals/signals_bsd.go

Purpose: BSD-family implementation of `setupSignals()` for progress refresh notifications.

Important APIs/types/functions: unexported `setupSignals()` registers `signals.ch` with `os/signal.Notify`.

Control flow: selected on `darwin`, `dragonfly`, `freebsd`, `netbsd`, and `openbsd`. It subscribes to both `syscall.SIGINFO` and `syscall.SIGUSR1`, allowing terminal status refresh from the platform's info key as well as explicit user signals.

State and persistence: no independent state; mutates only the global channel created in `signals.go`.

Dependencies/integration: depends on Go build tags, `os/signal`, and `syscall`. It is coupled to `GetProgressChannel()` because `signals.ch` must already exist.

Risks: signal names and availability are platform-specific; the build tag prevents accidental compilation elsewhere.

Test signals: direct signal behavior is not unit-tested, so build coverage on each BSD target is the main validation.
