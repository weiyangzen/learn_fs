# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult.go

## Purpose
Defines the compact ignore-match result type used by the ignore package without creating import cycles. It encodes whether a path is ignored, deletable, matched case-insensitively, or allows directory traversal to be skipped.

## Important APIs, Types, and Functions
`type R uint8` stores bit flags. Public constants are `NotIgnored`, platform-defined `Ignored`, `IgnoredDeletable`, and `IgnoreAndSkip`. Methods are `IsIgnored`, `IsDeletable`, `IsCaseFolded`, `CanSkipDir`, `ToggleIgnored`, `WithDeletable`, `WithFoldCase`, `WithSkipDir`, and `String`.

## Control Flow
All methods are direct bit tests or bit mutations. `IsDeletable` and `CanSkipDir` intentionally require the ignored bit in addition to their own flag bits, so orphaned modifier bits do not produce operational behavior.

## State and Persistence Behavior
No mutable or persistent state exists. Values are copied by value and used as return values from matcher calls.

## Dependencies and Integration Points
This package is imported by ignore matching code and downstream consumers such as folder scanning and deletion logic. Platform files define the meaning of the `Ignored` constant to apply default case folding on case-insensitive platforms.

## Risks
The type is intentionally tiny, so misuse risk comes from callers setting modifier bits without `ignoreBit`. The helper methods guard reads, but direct bit comparisons outside this package could bypass that contract. `String` is diagnostic only and should not be parsed as a stable wire format.

## Test Signals
`ignoreresult_test.go` verifies `CanSkipDir` requires an ignored result. Wider flag behavior is indirectly exercised by ignore matcher tests for deletable, case-insensitive, and skip-directory behavior.
