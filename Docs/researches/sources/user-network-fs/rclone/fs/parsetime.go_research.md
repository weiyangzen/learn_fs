# Research: sources/user-network-fs/rclone/fs/parsetime.go

## sources/user-network-fs/rclone/fs/parsetime.go

Purpose: implements `fs.Time`, a `time.Time` wrapper for flags, scanning, and JSON that accepts absolute timestamps, relative durations before now, and `"off"` as zero time. APIs include `Time`, `String`, `IsSet`, `ParseTime`, `Set`, `Type`, `UnmarshalJSON`, `MarshalJSON`, and `Scan`.

Control flow first handles `"off"`, then tries shared absolute date formats, then Go duration syntax, then custom duration suffixes. Relative durations subtract from `timeNowFunc`, so negative durations produce future times. JSON unmarshalling requires a string; marshalling delegates to `time.Time`, so zero time emits the Go zero timestamp rather than `"off"`. State is limited to the package-level `timeNowFunc` used by both duration and time parsing. Dependencies are standard JSON/time/fmt and parser helpers from `parseduration.go`. Risks include local timezone date parsing, surprising JSON zero-time output, mutable global time callback in tests, and permissive bare numeric string interpretation as seconds. Tests cover parse, string round-trip, scanner, JSON, and relative behavior.
