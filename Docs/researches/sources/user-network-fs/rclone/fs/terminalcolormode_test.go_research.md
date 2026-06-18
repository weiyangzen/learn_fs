# sources/user-network-fs/rclone/fs/terminalcolormode_test.go

## Purpose
This file tests the `TerminalColorMode` enum wrapper and, indirectly, the generic enum behavior used by rclone flag/config types.

## Important APIs, Flow, Risks, and Signals
`TestTerminalColorModeString` verifies known constants render as `"AUTO"`, `"ALWAYS"`, and `"NEVER"`, while an unknown ordinal renders as `Unknown(36)`. `TestTerminalColorModeSet` checks case-insensitive parsing and invalid input. `TestTerminalColorModeUnmarshalJSON` verifies JSON strings and numeric enum values are accepted when valid and rejected when invalid or out of range.

The tests are table-driven and create fresh enum variables per case. They depend on `encoding/json`, `strconv`, and `testify`. They protect config-file decoding, command-line flag parsing, and display behavior. Key risks covered are mixed-case input, invalid names, unknown enum values, and numeric JSON compatibility if enum ordinals change.
