# sources/sync-backup/syncthing/internal/slogutil/slogvalues.go

Purpose: Convenience constructors for common structured log attributes.

Important APIs/types/functions: `Address`, `Error`, `FilePath`, and `URI` return standardized slog attributes. `Error(nil)` returns an empty attribute so callers can pass it conditionally. Generic `Map` turns a map into sorted `[]any` slog args.

Control flow: `Map` sorts map keys with `slices.Sorted(maps.Keys(m))`, producing deterministic log attribute ordering.

State and persistence behavior: Stateless.

Dependencies and integration points: Used across API, beacon, support bundle, and other packages for consistent key names and deterministic map logging.

Risks: `Error(nil)` produces an empty key, which the formatter ignores; other handlers may represent it differently. `Map` allocates and is intended for logging convenience, not hot path data conversion.

Test signals: Deterministic map ordering is not directly tested here but affects stable log output.
