<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode.go -->
# sources/user-network-fs/rclone/fs/cutoffmode.go

## Purpose
Defines the `CutoffMode` enum controlling transfer cutoff behavior.

## Important APIs, Types, And Control Flow
`cutoffModeChoices` supplies choices `HARD`, `SOFT`, and `CAUTIOUS` to the generic `Enum` implementation. Constants map iota values to names and set `CutoffModeDefault` to hard.

## State And Persistence
Pure typed constants with no runtime state.

## Dependencies And Integration Points
Depends on the generic `Enum` helper for flag, scan, JSON, string, and help behavior. Used by configuration options that control cutoff semantics.

## Risks And Test Signals
Choice order is serialized by integer value, so reordering would break numeric compatibility. Tests cover string, set, and JSON paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/cutoffmode.go -->
