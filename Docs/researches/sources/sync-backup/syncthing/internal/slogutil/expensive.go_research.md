# sources/sync-backup/syncthing/internal/slogutil/expensive.go

Purpose: Deferred slog value wrapper for log attributes that are expensive to compute.

Important APIs/types/functions: `Expensive(fn func() any) expensive` returns a value implementing `slog.LogValuer` through `LogValue`, which calls `fn` only when slog resolves the value.

Control flow: No branching. `LogValue` delegates to the captured callback and wraps the result with `slog.AnyValue`.

State and persistence behavior: Stateless apart from the callback closure. No persistence.

Dependencies and integration points: Depends on `log/slog`. Intended for use with Syncthing's `formattingHandler`, which calls `Value.Resolve()` only after the record has passed handler/package-level filtering.

Risks: The callback can still run more than once if a value is resolved more than once. Callback side effects would be risky. Nil callbacks will panic on resolution.

Test signals: No direct test in this subset. A useful test would assert the callback is not invoked for a filtered-out debug message.
