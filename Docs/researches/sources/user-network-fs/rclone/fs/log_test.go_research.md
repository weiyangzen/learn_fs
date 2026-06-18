# sources/user-network-fs/rclone/fs/log_test.go

## Purpose
`log_test.go` tests core logging value and log-level parsing behavior from `fs/log.go`.

## Important APIs, types, and functions
The tests cover `LogValue`, `LogValueHide`, `LogValueItem.String`, `LogLevel.String`, `LogLevel.Set`, and JSON unmarshalling into `LogLevel`. Interface checks assert `LogLevel` satisfies rclone flag interfaces and `LogValueItem` satisfies `fmt.Stringer`.

## Control flow
`TestLogValue` compares visible and hidden rendering, including a value implementing `String()`. Level tests are table-driven for valid names, unknown names, numeric JSON values, invalid JSON strings, and out-of-range numbers.

## State and persistence behavior
No persistent state is used. Tests only construct values and unmarshal JSON in memory.

## Dependencies and integration points
The suite depends on `encoding/json`, `strconv`, testify, and rclone's enum/flag support. It protects CLI/config parsing for `--log-level` and structured logging argument rendering.

## Risks and edge cases
Hidden log values returning empty strings is important for text logs while still allowing structured fields elsewhere. JSON numeric parsing must reject invalid and out-of-range values rather than silently accepting bad log levels.

## Test signals
Coverage is focused on parsing and rendering; it does not test actual log emission, fatal/panic behavior, or handler integration, which are covered elsewhere or by integration tests.

Source-read signal: reviewed complete local file (95 lines). Types observed: `withString`. Functions/methods observed: `String`, `TestLogValue`, `TestLogLevelString`, `TestLogLevelSet`, `TestLogLevelUnmarshalJSON`.
