<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum.go -->
# sources/user-network-fs/rclone/fs/enum.go

## Purpose
Generic enum helper for byte-backed option types with string choices.

## Important APIs, Types, And Control Flow
`Enum[C Choices]` obtains choices from zero value `C`. It implements `String`, `Choices`, `Help`, case-insensitive `Set`, `Type` with optional `typer` override, `Scan`, JSON unmarshal from strings or numeric indexes, and JSON marshal as the string form.

## State And Persistence
Pure value methods. Numeric JSON values directly set enum indexes after range validation.

## Dependencies And Integration Points
Used by `CutoffMode` and other typed config options. Integrates with rclone flagger interfaces and `UnmarshalJSONFlag`.

## Risks And Test Signals
Choice order is ABI/config compatible because numeric input maps to indexes. Unknown enum values stringify as `Unknown(n)` and will marshal that string. Generic tests cover the core behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/enum.go -->
