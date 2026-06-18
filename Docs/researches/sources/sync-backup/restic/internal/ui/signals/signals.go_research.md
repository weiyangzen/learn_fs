# sources/sync-backup/restic/internal/ui/signals/signals.go

Purpose: defines the shared progress-signal entry point for restic UI code. `GetProgressChannel()` lazily creates a buffered `chan os.Signal` and calls the platform-specific `setupSignals()` selected by build tags.

Important APIs/types/functions: the only exported API is `GetProgressChannel() <-chan os.Signal`. Package state is a single anonymous global `signals` containing the channel and `sync.Once`.

Control flow: callers receive the same channel on every call. `sync.Once` prevents duplicate `signal.Notify` registration and keeps initialization race-safe.

State and persistence: process-local global state only; no filesystem persistence. The buffer size is one, so bursts can coalesce at the signal package boundary.

Dependencies/integration: integrates with platform files in the same package and with command progress display code that wants a user-triggered refresh.

Risks: the inline comment is important: because one global channel is shared, only one listener consumes each delivered signal. Multiple consumers must fan out externally.

Test signals: no direct tests here; behavior is implicitly covered by platform builds and consumers of the progress signal channel.
