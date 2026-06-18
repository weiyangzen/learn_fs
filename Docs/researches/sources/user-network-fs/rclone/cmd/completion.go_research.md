<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/completion.go -->
# sources/user-network-fs/rclone/cmd/completion.go

## Purpose

`completion.go` provides dynamic shell argument completion for rclone paths, combining configured remotes, local filesystem entries, and remote directory entries.

## Important APIs, Types, and Functions

`compLogf` writes Cobra completion debug messages. `addRemotes` completes configured remote names. `addLocalFiles` lists local directories and appends path separators for directories. `addRemoteFiles` parses the parent remote, opens it through `cache.Get`, lists root entries, and appends slash/no-space for directories. `validArgs` is the Cobra completion callback that chooses local/remotes until a valid remote path is detected, then remote entries.

## Control Flow

Completion detects whether `toComplete` parses as a remote with a colon. Without a valid remote it returns remote names and local paths; with a remote it lists remote entries. A disabled colon workaround remains as dead compatibility code.

## State and Persistence Behavior

It reads config sections, local directories, and remote listings. It does not persist state.

## Dependencies and Integration Points

It integrates with Cobra shell completion, `fs/config`, `fspath`, Fs cache, local OS directory APIs, and remote `List`.

## Risks and Test Signals

Risks include slow or side-effecting remote completion, config secrets in debug logs, path separator inconsistencies, remote parse edge cases, and stale colon workaround behavior. Tests should cover remote-name prefixes, local directory completion, remote file/directory completion, errors from parse/cache/list, and no-space directives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/completion.go -->
