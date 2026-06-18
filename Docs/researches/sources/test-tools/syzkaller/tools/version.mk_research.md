# sources/test-tools/syzkaller/tools/version.mk

## Purpose

`version.mk` is a Makefile fragment that builds version metadata flags for syzkaller tools. It embeds the current git revision and optional build commit metadata into Go linker flags.

## Important APIs, Types, and Functions

The fragment defines `GITREV`, `VERSION`, appends to `GOFLAGS`, and optionally appends `-X github.com/google/syzkaller/pkg/build.Commit=$(BUILD_COMMIT)`. It invokes `git rev-parse HEAD` through `$(shell ...)`.

## Control Flow

Make evaluates `GITREV`, constructs `VERSION` as a linker `-X` assignment to `pkg/build.gitRevision`, appends it to `GOFLAGS`, and conditionally appends the build commit assignment when `BUILD_COMMIT` is non-empty.

## State and Persistence Behavior

It does not write files; it affects build command state through Make variables and Go linker flags. The resulting binaries persist the selected revision strings.

## Dependencies and Integration Points

It integrates Make-based tool builds with `pkg/build` variables in Go code and depends on being run inside a git checkout.

## Risks and Test Signals

Outside a git repository, `GITREV` may be empty or contain command diagnostics depending on shell behavior. Quoting is minimal, so values should remain simple commit identifiers. Test signals are built binaries reporting expected revision metadata with and without `BUILD_COMMIT`.
