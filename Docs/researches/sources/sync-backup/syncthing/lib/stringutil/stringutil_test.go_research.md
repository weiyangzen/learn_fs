# sources/sync-backup/syncthing/lib/stringutil/stringutil_test.go

Purpose: validates order-preserving uniqueness after space trimming.

Important tests: `TestUniqueStrings` covers distinct values, duplicate values, repeated duplicates, nil input, and strings padded with ASCII spaces. It checks both length and positional equality.

State and persistence: no state.

Dependencies and integration: white-box package test with only `testing`.

Risks and signals: covers `UniqueTrimmedStrings` behavior but not `NiceDurationString`, Unicode whitespace, empty strings, or mixed tabs/newlines.
