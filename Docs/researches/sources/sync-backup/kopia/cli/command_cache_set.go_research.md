# sources/sync-backup/kopia/cli/command_cache_set.go

## Purpose
Cache configuration command that updates repository client cache limits and directory settings through direct repository parameters.

## APIs, Types, and Functions
Important APIs include types `cacheSizeFlags`, `commandCacheSetParams`; functions/methods `setup`, `setup`, `run`; Kingpin command(s) set: Sets parameters local caching of repository data; flags content-cache-size-mb: Desired size of local content cache (soft limit), content-cache-size-limit-mb: Maximum size of local content cache (hard limit), content-min-sweep-age: Minimal age of content cache item to be subject to sweeping, metadata-cache-size-mb: Desired size of local metadata cache (soft limit), metadata-cache-size-limit-mb: Maximum size of local metadata cache (hard limit), metadata-min-sweep-age: Minimal age of metadata cache item to be subject to sweeping, index-min-sweep-age: Minimal age of index cache item to be subject to sweeping, max-list-cache-duration: Duration of index cache, cache-directory: Directory where to store cache files.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Sets parameters local caching of repository data, binds flags content-cache-size-mb: Desired size of local content cache (soft limit), content-cache-size-limit-mb: Maximum size of local content cache (hard limit), content-min-sweep-age: Minimal age of content cache item to be subject to sweeping, metadata-cache-size-mb: Desired size of local metadata cache (soft limit), metadata-cache-size-limit-mb: Maximum size of local metadata cache (hard limit), metadata-min-sweep-age: Minimal age of metadata cache item to be subject to sweeping, index-min-sweep-age: Minimal age of index cache item to be subject to sweeping, max-list-cache-duration: Duration of index cache, plus 1 more, then runs through a repository writer action. The implementation persists maintenance parameters. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/content plus external packages context, time, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_cache_set_test.go` provides direct coverage.
