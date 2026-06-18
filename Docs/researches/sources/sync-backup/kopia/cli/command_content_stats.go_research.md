# sources/sync-backup/kopia/cli/command_content_stats.go

## Purpose
Content statistics command that summarizes content count and sizes, optionally including deleted entries and pack/blob distribution.

## APIs, Types, and Functions
Important APIs include types `commandContentStats`, `contentStatsTotals`; functions/methods `setup`, `run`, `calculateStats`; Kingpin command(s) stats: Content statistics; flags raw: Raw numbers.

## Control Flow, State, and Persistence
Control flow registers command(s) stats: Content statistics, binds flags raw: Raw numbers, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strconv, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/compression, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/compression, kopia/repo/content plus external packages context, strconv, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
