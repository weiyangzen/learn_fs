<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/internal.go -->
# sources/user-network-fs/rclone/cmd/test/info/internal/internal.go

Source read: complete file, 156 lines, 3233 bytes, sha256 `0b854873b214b4807d2748a45742955ebfb0fb9e074448c583655a0a16ab0f8d`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/internal/internal.go_research.md`.

## Purpose
Defines shared data types and JSON/text encodings for `rclone test info` reports.

## Important APIs, types, and functions
`Presence`, `Position`, constants, `PositionList`, `ControlResult`, and `InfoReport` model control-character results and backend capability booleans. `String`, marshal, and unmarshal methods provide stable textual/JSON representations.

## Control flow
Positions marshal as text map keys such as `left,middle`; presence values marshal as JSON strings such as `present` or `renamed`.

## State and persistence behavior
No runtime state beyond values being encoded/decoded.

## Dependencies and integration points
Depends on bytes, JSON, string parsing, and fmt errors.

## Risks and edge cases
Unmarshal errors currently format `%s` with the receiver in some cases, which may not show the raw unknown string clearly. Invalid bitmasks panic in `Position.String`.

## Test signals
Used by info command JSON output and CSV builder; encoding stability is the main compatibility signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/internal.go -->
