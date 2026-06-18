# sources/sync-backup/kopia/cli/command_cache_info.go

## Purpose
Cache information command that prints configured cache directories, usage, limits, and optional path-only output.

## APIs, Types, and Functions
Important APIs include types `commandCacheInfo`; functions/methods `setup`, `run`; Kingpin command(s) info: Displays cache information and statistics; flags path: Only display cache path.

## Control Flow, State, and Persistence
Control flow registers command(s) info: Displays cache information and statistics, binds flags path: Only display cache path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, os, path/filepath, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/content plus external packages context, fmt, os, path/filepath, time, plus 1 more.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
