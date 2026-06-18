# sources/sync-backup/kopia/internal/clock/now.go

Purpose: provides shared wall-clock normalization for Kopia clock abstractions by stripping Go's monotonic time component.

Important APIs/types/functions: private `discardMonotonicTime(time.Time) time.Time`.

Control flow: converts a `time.Time` to Unix nanoseconds and reconstructs it with `time.Unix(0, ...)`, preserving wall time while discarding monotonic metadata.

State and persistence behavior: no state or persistence. The normalized timestamp is suitable for persisted timestamps and long-duration wall-clock comparisons, including across system sleep.

Dependencies/integration: used by production and testing `Now` implementations. It avoids using monotonic durations where Kopia wants wall-clock duration semantics.

Risks/test signals: behavior depends on Unix nanosecond range and loses location information. It is indirectly tested through clock consumers and sleep/timing tests, not by a dedicated unit test here.
