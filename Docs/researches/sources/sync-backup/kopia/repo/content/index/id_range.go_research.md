# sources/sync-backup/kopia/repo/content/index/id_range.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/id_range.go_research.md`.

Purpose: models inclusive/exclusive ID ranges used by index and content iteration.

Important APIs: `IDRange` contains `StartID` and `EndID` prefixes. `Contains` checks an `ID` using `comparePrefix`. `PrefixRange` creates a range for all IDs beginning with a requested prefix by using `prefix + maxIDCharacterPlus1`. Predeclared ranges include `AllIDs`, `AllPrefixedIDs`, and `AllNonPrefixedIDs`.

Control flow, State and persistence: this is pure range logic. `maxIDCharacterPlus1` is `{` (`0x7B`), one byte after lowercase `z`, making it a convenient exclusive upper bound for valid ID characters.

Dependencies and integration: used by `Index.Iterate`, `Merged.Iterate`, `WriteManager.IterateContents`, and tests. Correct behavior depends on `ID.comparePrefix` preserving the same lexical order as encoded index keys.

Risks and tests: incorrect boundaries could silently omit or include content during listing, pack grouping, and garbage-collection scans. `merged_test.go` and `content_manager_test.go` exercise all IDs, prefixed-only, non-prefixed-only, explicit ranges, and exact prefix ranges.
