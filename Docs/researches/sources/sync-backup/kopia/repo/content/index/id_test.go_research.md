# sources/sync-backup/kopia/repo/content/index/id_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id_test.go_research.md`.

Purpose: unit-tests the `ID` and `IDPrefix` value semantics that all content index lookups depend on.

Important coverage: `TestIDValid` checks parsing, string formatting, JSON append truncation, JSON round trips, and pairwise ordering/compare-prefix behavior over empty, unprefixed, and prefixed IDs. `TestIDFromHash` validates construction from prefixes and max-length hashes. `TestParseInvalid` exercises too-short IDs, invalid hex, overlong hashes, and invalid prefixes. `TestIDPrefix`, `TestIDHash`, and `TestIDInvalidJSON` cover prefix validation, hash access, append output, `HasPrefix`, and malformed JSON.

Control flow, State and persistence: tests are pure and deterministic; they do not touch storage.

Dependencies and integration: uses `testify/require` and standard JSON formatting. These tests indirectly protect binary index code because ID ordering and prefix comparison must align with range and binary-search operations in v1/v2 indexes.

Risks and signal value: this file catches regressions in external JSON compatibility and internal ordering. It does not directly fuzz parse input beyond listed cases, but pack index fuzz tests add corrupted-binary coverage.
