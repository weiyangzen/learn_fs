# sources/sync-backup/kopia/internal/metricid/metricid_test.go

Purpose: validates built-in metric ID mappings for duplicate IDs, inverse consistency, consecutiveness, and max-index accuracy.

Important APIs/types/functions: `metricid.Counters`, `DurationDistributions`, `SizeDistributions`, `Mapping.NameToIndex`, `IndexToName`, and `MaxIndex`.

Control flow: `TestMappings` calls `verifyMapping` for each global mapping. The helper builds its own ID-to-name map, fails on duplicates, verifies every forward entry is present in the inverse mapping, and asserts the number of IDs equals the maximum ID.

State/persistence behavior: no state is persisted during tests. The tested data is persistent compatibility metadata, so failures indicate an unsafe mapping edit.

Dependencies/integration: uses `testify/require`. The empty size distribution mapping passes because both length and max are zero.

Risks/test signals: the test enforces consecutive positive IDs but not semantic stability of names assigned to existing IDs. Review is still required for renames.
