# sources/storage-engines/pebble/scripts/run-tests-with-custom-go.sh

## Purpose
This script builds or reuses a custom CockroachDB Go toolchain, then runs `go test -tags cockroach_go` for the provided arguments.

## Important APIs, Types, and Functions
It resolves `GO_SHA` directly or from `GO_BRANCH` with `git ls-remote`, caches toolchains under `${XDG_CACHE_HOME:-$HOME/.cache}/cockroachdb-go/$GO_SHA`, clones `https://github.com/cockroachdb/go.git`, builds with `src/make.bash`, sets `GOROOT` and `PATH`, and executes tests in `GITHUB_WORKSPACE` or the current directory.

## Control Flow
If the cached `go` binary is absent, it creates the cache directory, removes any partial checkout, clones and checks out the requested SHA, and builds the toolchain. It then exports the new Go path, prints `go version`, changes to the repo root, echoes the test command, and runs it.

## State and Persistence Behavior
Persistent state is the custom Go source/build cache. It may perform network clone and branch resolution. It does not modify repository source except through normal test side effects.

## Dependencies and Integration Points
It depends on git, Bash, Go bootstrap prerequisites, and CockroachDB's Go fork. It is designed for GitHub Actions and local runs.

## Risks
The default branch name is hard-coded. Cache corruption is handled only by removing the source tree when binary is missing, not by verifying an existing binary. Building Go is expensive and network-dependent. All caller arguments are passed to `go test` with the `cockroach_go` tag.

## Test Signals
Signal is the custom `go version` plus pass/fail from the target `go test` command.
