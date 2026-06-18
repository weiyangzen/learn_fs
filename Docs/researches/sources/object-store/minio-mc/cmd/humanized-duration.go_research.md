# sources/object-store/minio-mc/cmd/humanized-duration.go

Purpose: Converts `time.Duration` values into compact human-readable duration components and strings.

Important APIs/types/functions: `humanizedDuration`, `StringShort`, `String`, and `timeDurationToHumanizedDuration`.

Control flow: Conversion chooses milliseconds, seconds, minutes, hours, or days based on duration magnitude and fills remainder fields using `math.Mod`. String methods format short or full strings from populated fields.

State and persistence: Stateless.

Dependencies/integration: Used by status/progress/reporting code elsewhere that needs user-friendly elapsed time.

Risks: Does not handle negative durations specially. Pluralization is not grammatically adjusted for singular units. Milliseconds under one second are truncated.

Test signals: No direct tests.
