# sources/sync-backup/syncthing/lib/ignore/ignoreresult/ignoreresult_test.go

## Purpose
Verifies the semantic contract of the skip-directory result flag.

## Important APIs, Types, and Functions
`TestFlagCanSkipDir` constructs `ignoreresult.R` values including zero, `NotIgnored`, `NotIgnored.WithSkipDir`, `Ignored`, and `IgnoreAndSkip`.

## Control Flow
The test iterates table rows and compares `CanSkipDir()` with the expected boolean, reporting mismatches with the result string.

## State and Persistence Behavior
No state, persistence, filesystem, or network behavior.

## Dependencies and Integration Points
Imports `github.com/syncthing/syncthing/lib/ignore/ignoreresult` as an external test package, which validates the public API as callers see it.

## Risks
The test covers one important invariant but does not directly test `IsDeletable`, `IsCaseFolded`, mutator methods, or `String`; those are left to indirect ignore matcher tests.

## Test Signals
Protects callers that use `Match(...).CanSkipDir()` as a single check instead of separately checking `IsIgnored`.
