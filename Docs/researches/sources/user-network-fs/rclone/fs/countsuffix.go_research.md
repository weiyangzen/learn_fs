<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix.go -->
# sources/user-network-fs/rclone/fs/countsuffix.go

## Purpose
Implements `CountSuffix`, an int64 flag/config type for decimal count units (`k`, `M`, `G`, `T`, `P`, `E`) and `off`.

## Important APIs, Types, And Control Flow
`String` and `Unit` scale values to the largest decimal suffix with integer or three-decimal formatting. `Set` parses empty/error cases, `off`, byte suffixes, plain numbers defaulting to kilo, decimal values, and rejects negative values/bad suffixes. It implements `Type`, `Scan`, JSON unmarshalling through `UnmarshalJSONFlag`, and sortable `CountSuffixList`.

## State And Persistence
Pure value parsing/formatting with no external state. Negative values render as `off`.

## Dependencies And Integration Points
Used by flags/options needing count quantities rather than binary byte sizes. Integrates with rclone's flagger interfaces and JSON config parsing.

## Risks And Test Signals
Defaulting bare numbers to kilo can surprise callers expecting raw counts. Float-to-int truncation is implicit. Tests cover rendering, parsing, scanning, and string/numeric JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/countsuffix.go -->
