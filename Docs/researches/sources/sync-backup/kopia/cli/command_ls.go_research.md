# sources/sync-backup/kopia/cli/command_ls.go

## Purpose
Repository object listing command analogous to `ls`. It resolves snapshot/object paths and prints directory entries with long, recursive, human-readable, object-ID, and error-summary modes.

## APIs, Types, and Functions
Important APIs include types `commandList`; functions/methods `setup`, `run`, `listDirectory`, `printDirectoryEntry`, `nameToDisplay`; Kingpin command(s) list: List a directory stored in repository object.; flags long: Long output, human-readable: Show human-readable sizes, recursive: Recursive output, show-object-id: Show object IDs, error-summary: Emit error summary; arguments object-path: Path.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List a directory stored in repository object., binds flags long: Long output, human-readable: Show human-readable sizes, recursive: Recursive output, show-object-id: Show object IDs, error-summary: Emit error summary, accepts arguments object-path: Path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository connection/session state and command-local option fields. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/fs, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/object, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/repo, kopia/repo/object, kopia/snapshot/snapshotfs plus external packages context, fmt, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
