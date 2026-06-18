# sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/packindex_internal_test.go_research.md`.

Purpose: narrow internal test for binary `ID` encoding helpers.

Important coverage: `TestRoundTrip` converts `EmptyID`, an unprefixed ID, and a prefixed ID through `contentIDToBytes` and `bytesToContentID`, asserting exact equality. It also checks that nil bytes decode to `EmptyID`.

Control flow, State and persistence: pure unit test, no storage or pack index files. It reaches unexported helpers by being in package `index`.

Dependencies and integration: uses `mustParseID` helper from the broader pack index test file. The behavior under test is used by both v1 and v2 binary index keys.

Risks and signal value: this catches accidental changes to the prefix-plus-hash binary representation. It does not test oversized byte slices, which intentionally panic in `bytesToContentID`; corrupted index tests exercise broader defensive parsing.
