# sources/sync-backup/restic/cmd/restic/cmd_init_integration_test.go

Purpose: shared `init` test helper plus coverage for copying chunker parameters from a secondary repository.

Important APIs/types/functions: `testRunInit` lowers KDF cost and disables polynomial checks for tests, invokes `runInit`, and creates junk files in repository subdirectories; `TestInitCopyChunkerParams` validates `InitOptions.SecondaryRepoOptions` behavior.

Control flow and state: the helper creates a real local test repository and intentionally adds temporary junk files under index/snapshots/keys/locks/data to ensure later commands tolerate unknown files. The copy test initializes two repos, first expecting failure without `CopyChunkerParameters`, then success with it, then opens both repos to compare config polynomials.

Dependencies and integration points: relies on `withTestEnvironment`, `global.OpenRepository`, repository test hooks, and progress printers.

Risks: test code mutates repository directories directly, so it assumes local backend layout. It does not test JSON output or repository-version parsing.

Test signals: validates guardrail for secondary options and the exact config-level chunker polynomial copy.
