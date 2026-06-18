# sources/test-tools/syzkaller/pkg/updater/updater.go

## Purpose

`updater.go` maintains syzkaller self-updates and build artifacts for syz-ci-style deployments. It keeps `latest` and `current` syzkaller builds, rebuilds from the configured repository, and can restart the current executable after an update.

## Important APIs, Types, And Functions

`Updater` stores repo/build paths, artifact glob requirements, compiler ID, and config. `Config` controls update behavior, build semaphore, reporting, repository/branch/descriptions, targets, and make targets. `New` validates executable placement, prepares GOPATH-style source directory, computes expected output files, and captures `go version`. `UpdateOnStart`, `waitForUpdate`, `UpdateAndRestart`, `pollAndBuild`, `build`, and `checkLatest` implement the lifecycle.

## Control Flow, State, Dependencies, And Integration

The updater mutates the working directory: `gopath/src/github.com/google/syzkaller`, `syzkaller/latest`, `syzkaller/current`, and the current executable. It polls a `vcs.Repo`, runs `make`, per-target builds, and `go test -short ./...`, copies optional descriptions, writes a `tag` file, and links/copies required artifacts. Autoupdate mode starts a background waiter and closes `updatePending` when a new build is ready.

## Risks And Test Signals

This is operationally risky code: it removes `current`, copies over executables, can `syscall.Exec`, relies on external `go`/`make`, and serializes builds through `BuildSem`. Missing `BuildSem` would panic. Build failures are reported but only latest good builds are promoted. No direct tests are in this subset; integration depends on syz-ci environments and VCS/build helpers.
