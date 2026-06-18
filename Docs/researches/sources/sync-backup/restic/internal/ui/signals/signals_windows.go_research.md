# sources/sync-backup/restic/internal/ui/signals/signals_windows.go

Purpose: no-op signal setup for Windows builds where Unix progress signals are unavailable.

Important APIs/types/functions: unexported `setupSignals()` with an empty body.

Control flow: Go selects this file when the Unix build-tagged files do not match. `GetProgressChannel()` still creates a channel, but no OS signal is registered.

State and persistence: no state beyond the global channel allocated in `signals.go`.

Dependencies/integration: avoids importing `os/signal` or `syscall`, keeping Windows builds simple.

Risks: consumers waiting only for signal events will never receive them on Windows; they must also rely on timers or normal progress update paths.

Test signals: no direct tests; build coverage is the relevant signal.
