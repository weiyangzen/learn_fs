# Research: sources/user-network-fs/rclone/fs/parseduration_test.go

## sources/user-network-fs/rclone/fs/parseduration_test.go

Purpose: verifies `Duration` parsing, formatting, readable output, scanning, and JSON unmarshalling. It also asserts pointer and non-pointer flag interfaces.

Control flow uses table-driven tests with a fixed `now` callback for date-derived durations. It covers numeric defaults, Go duration syntax, custom suffixes, negative durations, `"off"`, absolute date formats, reverse `String` parsing, long and short readable strings, scanner input, JSON strings, JSON integer nanoseconds, invalid data, and max-int64 mapping to `DurationOff`. State mutation is limited to temporarily overriding `timeNowFunc` in scanner tests. Dependencies are `assert`, `require`, `encoding/json`, and `fmt.Sscan`. Integration points are config flags and rc/config JSON parsing that consume `Duration`. Risks highlighted include local-time tolerance for date tests, floating-point precision near `DurationOff`, and accepting raw integer JSON as nanoseconds. Test signal is strong for public conversion semantics.
