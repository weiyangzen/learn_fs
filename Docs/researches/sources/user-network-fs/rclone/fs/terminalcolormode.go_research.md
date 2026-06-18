# sources/user-network-fs/rclone/fs/terminalcolormode.go

## Purpose
This file defines the user-facing enum for terminal color handling. It models whether ANSI color should be selected automatically, never used, or always used.

## Important APIs, State, and Integration
`TerminalColorMode` is a type alias for `Enum[terminalColorModeChoices]`. Constants are `TerminalColorModeAuto`, `TerminalColorModeNever`, and `TerminalColorModeAlways`. The unexported `terminalColorModeChoices` type provides `Choices() []string`, mapping enum ordinals to `"AUTO"`, `"NEVER"`, and `"ALWAYS"`. There is no runtime control flow beyond enum choice lookup; parsing, JSON handling, and unknown-value formatting are supplied by the generic `Enum` implementation elsewhere in `fs`.

The type integrates with rclone's configuration and flag system through the generic enum methods. The main risk is ordinal stability because the choices slice uses constants as indexes. Adding or reordering values can change serialized numeric meanings. Tests in `terminalcolormode_test.go` cover string output, case-insensitive parsing, JSON strings, JSON numeric ordinals, and invalid values.
