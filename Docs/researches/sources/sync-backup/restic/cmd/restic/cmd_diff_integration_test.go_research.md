# sources/sync-backup/restic/cmd/restic/cmd_diff_integration_test.go

Purpose: integration tests for snapshot diff output and JSON format.

Important helpers/tests: `setupDiffRepo` creates a repository with two snapshots containing renamed, added, removed, and modified files/directories. `TestDiff` verifies invalid snapshot handling, regex patterns for text output, summary counts, and quiet mode shortening. `TestDiffJSON` parses line-delimited JSON, counts change messages, checks final `DiffStatsContainer`, and verifies quiet JSON emits only statistics.

State/persistence: creates/modifies temp filesystem content, runs backups, and reads diff output.

Dependencies/integration: backup helpers, snapshot map helpers, captured stdout, JSON decoding, and regex matching.

Risks/test signals: regexes are coupled to human-readable output. JSON tests provide a more stable contract for automated consumers.
