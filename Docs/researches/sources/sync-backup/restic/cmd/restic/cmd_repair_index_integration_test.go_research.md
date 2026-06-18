# sources/sync-backup/restic/cmd/restic/cmd_repair_index_integration_test.go

Purpose: integration coverage for index rebuild and related failure modes.

Important APIs/types/functions: `testRunRebuildIndex`; `testRebuildIndex`; `indexErrorBackend`; `errorReadCloser`; `appendOnlyBackend`; `TestRebuildIndex`; `TestRebuildIndexDamage`; `TestRebuildIndexFailsOnAppendOnly`.

Control flow and state: tests load a fixture repo with duplicate packs in indexes, verify `check` suggests `restic repair index`, run rebuild, and verify check becomes silent. Damage test corrupts the first index during load to ensure repair can tolerate bad index reads. Append-only test wraps backend removal to fail and expects rebuild failure.

Dependencies and integration points: uses backend wrappers, checker output, fixture tar repos, and repository commands.

Risks: output substring checks are coupled to checker messages. Backend wrappers simulate only specific corruption/removal failures.

Test signals: validates that repair index fixes duplicated index entries, handles index read corruption, and reports append-only constraints.
