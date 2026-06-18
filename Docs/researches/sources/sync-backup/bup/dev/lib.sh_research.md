# sources/sync-backup/bup/dev/lib.sh

## Purpose
Shared Bash helper library for bup development/test scripts.

## Important APIs, Types, and Functions
Defines `bup_dev_lib_top`, `bup_exit_failure`, `bup-cfg-py`, `bup-python`, `force-delete`, `resolve-parent`, `path-filesystems`, and `escape-erx`.

## Control Flow
Functions dispatch through repository-local dev executables, resolve parents through `bup.helpers.resolve_parent`, walk from a directory to root to print filesystem types, and escape regex metacharacters via sed.

## State and Persistence Behavior
No direct persistence. `force-delete` delegates destructive deletion.

## Dependencies and Integration Points
Sourced by Bash scripts that assume pipefail and source-tree cwd. Bridges shell tooling to configured bup Python.

## Risks and Test Signals
Risks are sourcing from wrong cwd and shell quoting around paths. Signals are correct helper outputs and successful delegated commands.
