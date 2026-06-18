<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/config.go -->
# sources/sync-backup/kopia/cli/config.go

## Purpose
Contains shared application helpers for repository opening, config path resolution, fatal/termination callbacks, local filesystem entry construction, and OS detection.

## Important APIs, Types, And Functions
Key functions are `onRepositoryFatalError`, `onTerminate`, `openRepository`, `optionsFromFlags`, `repositoryConfigFileName`, `resolveSymlink`, `getLocalFSEntry`, and `isWindows`.

## Control Flow
`openRepository` checks config existence, optionally reports update notices, obtains a password from flags/persistence/prompt, opens the repository with constructed options, and maps missing config to user-friendly errors. `onTerminate` registers signal or simulated Ctrl-C callbacks.

## State And Persistence Behavior
Persistent state includes the repository config file path and password persistence lookups; this file does not write repository data. `optionsFromFlags` installs fatal-error callbacks that can terminate the process.

## Dependencies And Integration Points
Integrates `repo.Open`, localfs, ospath config directories, password helpers, update checks, signal handling, and test-only simulated Ctrl-C.

## Risks And Edge Cases
`onTerminate` creates a new signal subscription per callback and does not stop notification. Symlink resolution affects snapshot source identity. Fatal error callbacks call `exitWithError`, so tests must override it carefully.

## Test Signals
Tests should cover config path resolution, required versus optional repository open, symlink resolution, password source precedence, and simulated termination callbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/config.go -->
