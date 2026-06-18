## sources/sync-backup/kopia/fs/utc_timestamp.go

Purpose: defines a compact UTC nanosecond timestamp type with JSON and time arithmetic helpers.

Important APIs/types/functions: `UTCTimestamp`, `MarshalJSON`, `UnmarshalJSON`, `ToTime`, `Add`, `Sub`, `After`, `Before`, `Equal`, `Format`, and `UTCTimestampFromTime`.

Control flow, state, and persistence: stores `time.Time.UnixNano()` as an `int64`. JSON unmarshalling delegates to `time.Time.UnmarshalJSON`, then stores the absolute instant; marshaling formats through `ToTime().UTC()`. Persistence format is a JSON timestamp string, not a raw integer.

Dependencies and integration points: used by filesystem/snapshot data needing stable UTC JSON representation.

Risks and test signals: risks include timezone expectations and nanosecond precision. Tests cover JSON round trip, timezone normalization, comparisons, duration arithmetic, formatting, and invalid JSON error wrapping.
