<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version.go -->
# sources/user-network-fs/rclone/cmd/version/version.go

## Purpose

`version.go` implements `rclone version`, including normal build/runtime version display, online update checks, and dependency/build-info dumping.

## Important APIs, Types, and Functions

Flags are `check` and `deps`. `stripV` normalizes semver strings. `GetVersion` fetches `version.txt`, trims rclone/beta decorations, parses `Last-Modified`, and returns a semver. `CheckVersion` compares current, latest, and beta versions. `printModule` and `printDependencies` format Go build info.

## Control Flow

The command accepts no args. With `--deps` it reads build info from `os.Args[0]`. With `--check` it performs HTTP GETs through rclone's configured HTTP client. Otherwise it delegates to `cmd.ShowVersion`.

## State and Persistence Behavior

The file is read-only except stdout/stderr output and network requests. It consumes global `fs.Version`, process args, and HTTP config but does not persist data.

## Dependencies and Integration Points

It integrates with Cobra, `cmd.ShowVersion`, `fshttp`, `coreos/go-semver`, Go `debug/buildinfo`, and rclone config-aware HTTP behavior.

## Risks and Test Signals

Risks include network failures, malformed version text, missing `Last-Modified`, beta suffix trimming, semver incompatibility for dev versions, and build-info absence in unusual binaries. Tests should mock update endpoints and cover `--deps`, dev versions, inaccessible config files, and stdout handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version.go -->
