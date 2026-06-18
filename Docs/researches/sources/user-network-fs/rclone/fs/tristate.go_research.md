# sources/user-network-fs/rclone/fs/tristate.go

## Purpose
This file implements `Tristate`, a nullable boolean used by configuration and flag code when `true`, `false`, and unset must be distinguished.

## Important APIs, Flow, State, and Integration
`Tristate` has `Value bool` and `Valid bool`. `String` returns `"unset"` when invalid and `"true"` or `"false"` when valid. `Set` lowercases input, treats `""`, `"nil"`, `"null"`, and `"unset"` as invalid/unset, and otherwise delegates to `strconv.ParseBool`. `Type` returns `"Tristate"`. `Scan` tokenizes input and calls `Set`. `UnmarshalJSON` decodes into `*bool`, mapping JSON `null` to unset and booleans to valid values. `MarshalJSON` writes `null` for unset or a boolean for valid values.

All behavior is local to the value. The main risk is callers reading `Value` without checking `Valid`; `Set` can clear validity without resetting the old value. The type integrates with `Flagger`/`FlaggerNP`, JSON config serialization, and scanner-based parsing. Tests cover interface satisfaction, string rendering, text parsing, scanning, JSON unmarshal, invalid JSON, and JSON marshal output.
