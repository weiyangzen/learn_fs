<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_show.go -->
# sources/sync-backup/kopia/cli/command_show.go

## Purpose
Implements `kopia show`/`cat`, which opens a repository object by object ID or object-path syntax and streams its bytes to stdout.

## Important APIs, Types, And Functions
Defines `commandShow` with `path` and text output. `run` uses `snapshotfs.ParseObjectIDWithPath`, `repo.OpenObject`, and `iocopy.JustCopy`.

## Control Flow
At execution the object path argument is parsed, the repository object reader is opened, deferred closed, and copied directly to stdout.

## State And Persistence Behavior
It does not mutate repository data. State is limited to the opened object reader and stdout stream; object identity can include nested snapshotfs path parsing.

## Dependencies And Integration Points
Depends on repository reader actions, `snapshotfs` object ID parsing, and the internal copy helper.

## Risks And Edge Cases
Large objects stream without buffering, but binary output goes directly to stdout. Parse errors and open errors include user input in messages. Consumers must not expect decompression or JSON formatting here; that is handled by other show utilities.

## Test Signals
Test signals are object parse/open failure tests and a successful copy of known object content, including binary-safe output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_show.go -->
