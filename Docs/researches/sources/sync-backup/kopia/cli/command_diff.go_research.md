# sources/sync-backup/kopia/cli/command_diff.go

## Purpose
Snapshot diff command that compares two repository object paths and reports added, removed, changed, and metadata-different filesystem entries.

## APIs, Types, and Functions
Important APIs include types `commandDiff`; functions/methods `setup`, `run`, `defaultDiffCommand`; Kingpin command(s) diff: Displays differences between two repository objects (files or directories); flags files: Compare files by launching diff command for all pairs of (old,new), stats-only: Displays only aggregate statistics of the changes between two repository objects, diff-command: Displays differences between two repository objects (files or directories); arguments object-path1: First object/path, object-path2: Second object/path.

## Control Flow, State, and Persistence
Control flow registers command(s) diff: Displays differences between two repository objects (files or directories), binds flags files: Compare files by launching diff command for all pairs of (old,new), stats-only: Displays only aggregate statistics of the changes between two repository objects, diff-command: Displays differences between two repository objects (files or directories), accepts arguments object-path1: First object/path, object-path2: Second object/path, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository connection/session state and command-local option fields. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, encoding/json, fmt, strings, github.com/pkg/errors, github.com/kopia/kopia/fs, github.com/kopia/kopia/internal/diff, github.com/kopia/kopia/repo, github.com/kopia/kopia/snapshot/snapshotfs. It integrates with Kopia repository internals such as kopia/fs, kopia/internal/diff, kopia/repo, kopia/snapshot/snapshotfs plus external packages context, encoding/json, fmt, strings, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
