# sources/sync-backup/syncthing/lib/syncutil/timeoutcond.go

Purpose: condition-variable-like primitive that supports broadcast wakeups with waiter-specific timeouts.

Important APIs and control flow: `NewTimeoutCond` stores a caller-supplied locker. `Broadcast` must be called while locked; if a channel exists, it closes it and resets to nil, waking all current waiters. `SetupWait` creates a waiter with a `time.Timer`. `Wait` must be called while locked; it lazily creates the shared channel, unlocks around the select, then re-locks before returning true on broadcast or false on timer expiry. `Stop` stops the timer when the waiter is no longer needed.

State and persistence: in-memory locker, shared channel, and timers.

Dependencies and integration: useful where `sync.Cond` semantics need timeouts without per-wait goroutines.

Risks: callers must obey locking requirements. Timer channels are not drained in `Stop`, so reuse is not supported. Broadcasts before a waiter captures the channel are not remembered, matching cond semantics. Tests exercise timing and deadlock behavior.
