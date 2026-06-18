# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_foldcase.go

## Purpose
Supplies the platform-specific default ignored result for case-insensitive filesystems and operating systems.

## Important APIs, Types, and Functions
Defines `const Ignored = ignoreBit | foldCaseBit` behind the `windows || darwin || ios` build tag.

## Control Flow
There is no runtime control flow. The Go build selects this file on Windows, Darwin, and iOS, causing plain ignored matches to also report `IsCaseFolded`.

## State and Persistence Behavior
No state or persistence. The constant affects matcher return values at compile time.

## Dependencies and Integration Points
Used by `ignoreresult.go` constants such as `IgnoredDeletable` and `IgnoreAndSkip`, and by ignore matcher code that starts from `ignoreresult.Ignored`.

## Risks
The correctness boundary is build-tag selection. If a platform has case-sensitive matching despite these OS defaults, callers may get folded behavior unless they use explicit ignore flags or platform-specific logic.

## Test Signals
`ignore_test.go` includes platform-gated case-insensitivity tests that should pass on Windows and Darwin builds.
