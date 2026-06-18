# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_nofoldcase.go

## Purpose
Supplies the platform-specific default ignored result for platforms where ignore matching should not automatically be case-folded.

## Important APIs, Types, and Functions
Defines `const Ignored = ignoreBit` behind the `!windows && !darwin && !ios` build tag.

## Control Flow
No runtime control flow. The Go build selects this file on non-Windows, non-Darwin, non-iOS platforms.

## State and Persistence Behavior
No state or persistence. The constant only influences compiled matcher behavior.

## Dependencies and Integration Points
Complements `ignoreresult_foldcase.go` and feeds constants in `ignoreresult.go`. Ignore matcher tests on Unix-like case-sensitive builds expect uppercase and lowercase names to remain distinct unless patterns request `(?i)`.

## Risks
The default assumes OS-level case sensitivity. Mounted case-insensitive filesystems on Unix-like platforms may still need explicit case-insensitive ignore patterns.

## Test Signals
`TestCaseSensitivity` in `ignore_test.go` checks that non-Windows/non-Darwin builds do not match different case by default.
