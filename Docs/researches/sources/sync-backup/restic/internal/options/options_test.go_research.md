## sources/sync-backup/restic/internal/options/options_test.go

Purpose: unit tests for the backend extended-options parser and reflector.

Important tests: `TestParseOptions` covers whitespace trimming, lowercasing, missing values, embedded equals in values, and duplicate equal values. `TestParseInvalidOptions` covers empty keys and conflicting duplicates. `TestOptionsExtract` verifies namespace filtering. `TestOptionsApply` and `TestOptionsApplyInvalid` validate typed reflection assignment and conversion errors. `TestListOptions` and `TestAppendAllOptions` check tag discovery and namespace/name sorting.

Control flow and state: tests use local structs with `option` and `help` tags. Invalid duration errors are matched by regexp to allow Go-version wording variance.

Dependencies and integration points: validates behavior used by global backend config application. No external backend is required.

Risks and test signals: tests protect accepted CLI syntax and error messages but do not cover panic paths for duplicate struct tags or unsupported field types.
