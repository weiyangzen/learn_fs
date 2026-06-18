# sources/test-tools/syzkaller/pkg/vcs/fuchsia.go

## Purpose

`fuchsia.go` adapts the generic VCS interface for Fuchsia checkouts, where repository setup uses Jiri/bootstrap rather than a plain Git clone.

## Important APIs, Types, And Functions

`fuchsia` stores a directory and embedded `gitRepo`. `newFuchsia` appends `OptPrecious` to avoid destructive cleanup. `Poll` accepts only the Fuchsia main repository and `main`/`master`, runs `jiri update`, initializes on failure, and returns `HEAD`. `initRepo` bootstraps through a curl/base64/bash pipeline and runs `jiri update`. Most other `Repo` methods delegate to `gitRepo`; `PushCommit` returns not implemented.

## Control Flow, State, Dependencies, And Integration

Initialization removes and replaces the checkout directory through a temporary directory. It uses sandboxed command execution for bootstrap and Jiri. The adapter is selected by `NewRepo` for Fuchsia and Linux/Starnix. Persistent state is the checkout itself.

## Risks And Test Signals

The bootstrap command depends on network, curl, base64, bash, and upstream script stability. The first bootstrap `jiri update` error is intentionally ignored. Because repos are precious, generic recovery cleanup is disabled. No direct tests are in this subset.
