# sources/sync-backup/kopia/cli/command_cache_clear.go

## Purpose
Cache-clearing command for local repository caches. It selects partial cache directories, removes files/directories with retry behavior, and reports cleanup errors.

## APIs, Types, and Functions
Important APIs include types `commandCacheClear`; functions/methods `setup`, `run`, `clearCacheDirectory`; Kingpin command(s) clear: Clears the cache; flags partial: Specifies the cache to clear.

## Control Flow, State, and Persistence
Control flow registers command(s) clear: Clears the cache, binds flags partial: Specifies the cache to clear, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, path/filepath, github.com/pkg/errors, github.com/kopia/kopia/internal/cache, github.com/kopia/kopia/internal/retry, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/cache, kopia/internal/retry, kopia/repo plus external packages context, os, path/filepath, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: filesystem operations are platform and permission sensitive. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
