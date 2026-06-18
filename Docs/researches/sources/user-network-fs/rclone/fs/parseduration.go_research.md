# Research: sources/user-network-fs/rclone/fs/parseduration.go

## sources/user-network-fs/rclone/fs/parseduration.go

Purpose: implements `fs.Duration`, a flag/JSON/scanner-friendly duration type with rclone-specific suffixes and date parsing. APIs include `Duration`, `DurationOff`, `String`, `IsSet`, `ParseDuration`, readable string variants, `Set`, `Type`, `UnmarshalJSON`, and `Scan`.

Control flow parses `"off"`, Go durations, custom suffixes (`d`, `w`, `M`, `y`, default seconds), and absolute dates interpreted as duration before an epoch. Formatting chooses larger suffixes for `String`, while `readableString` decomposes into years/weeks/days/hours/minutes/seconds/milliseconds with optional truncation. JSON accepts strings or integer nanoseconds. State is none except package-level suffix and date format tables, and shared `timeNowFunc` from time parsing. Dependencies are standard `time`, `encoding/json`, `strconv`, and `fmt.Scanner`. Risks include approximate month/year definitions, local timezone date parsing, float conversions near max duration, empty string parse errors, and off sentinel collisions with max int64. Tests cover parsing, formatting round-trips, JSON, scanner, negatives, and readable strings.
