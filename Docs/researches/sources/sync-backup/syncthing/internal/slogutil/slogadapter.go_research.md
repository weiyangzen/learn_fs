# sources/sync-backup/syncthing/internal/slogutil/slogadapter.go

Purpose: Compatibility adapter from Syncthing's older debug logging style to `log/slog`, plus package registration.

Important APIs/types/functions: `RegisterPackage` and `NewAdapter` derive the caller package from the runtime stack and register a description. `adapter` exposes `Debugln`, `Debugf`, and `ShouldDebug`. Internal `log` builds a `slog.Record` with the caller PC and sends it to the underlying handler.

Control flow: Debug methods format the message, check handler enablement, capture the caller PC with `runtime.Callers(3, ...)`, and invoke `Handle` on the default slog handler. `ShouldDebug` asks `globalLevels` for the facility level.

State and persistence behavior: Registers package descriptions in global in-memory log-level state. No persistence.

Dependencies and integration points: Used by packages such as API and beacon to keep `l.Debugf`/`l.Debugln` calls while using slog formatting and filtering.

Risks: Caller skip depths are fragile; wrapper changes can misattribute package names. Only debug-level logging is implemented by the adapter.

Test signals: Formatter test indirectly verifies package attribution for logs from `slogutil`.
