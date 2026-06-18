# sources/sync-backup/syncthing/internal/slogutil/leveler.go

Purpose: Tracks per-package log levels and descriptions, including compatibility with the traditional `STTRACE` package override format.

Important APIs/types/functions: Public functions expose package descriptions/levels and set package/default levels: `PackageDescrs`, `PackageLevels`, `SetPackageLevel`, `SetDefaultLevel`, and `SetLevelOverrides`. `levelTracker` stores `defLevel`, package descriptions, and package-specific level overrides under an RW mutex.

Control flow: `SetLevelOverrides` splits comma-separated input, defaults each listed package to DEBUG, and optionally parses `pkg:LEVEL` via `slog.Level.UnmarshalText`. `levelTracker.Get` returns explicit levels or the default. Setters log an info message when a value changes. `Levels` returns a map for all registered descriptions, using defaults where no explicit override exists.

State and persistence behavior: In-memory global state only. Changes affect log filtering immediately but are not persisted here.

Dependencies and integration points: Used by `formattingHandler` to filter records by caller package. `slogadapter.RegisterPackage` and `NewAdapter` register descriptions. REST API endpoints expose and mutate levels through `/rest/system/loglevels`.

Risks: `SetLevelOverrides` logs warnings through the same logging system it configures, so bad early configuration could be noisy. The `Levels` snapshot only includes described packages, not arbitrary package strings set without descriptions.

Test signals: Indirectly tested by formatter output and API log-level endpoint tests. Dedicated tests should cover STTRACE parsing and invalid levels.
