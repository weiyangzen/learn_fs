# sources/user-network-fs/rclone/backend/sharefile/update-timezone.sh

## Purpose

This helper regenerates the embedded ShareFile timezone data used by `tzdata_vfsdata.go`. It extracts only `America/New_York` from Go's bundled zoneinfo and runs the backend generator.

## Important APIs, Types, and Functions

The script uses `go env GOROOT` to locate `lib/time/zoneinfo.zip`, `unzip` to extract `America/New_York`, `go run generate_tzdata.go` to create the generated Go asset file, and `rm -rf tzdata` for cleanup.

## Control Flow

With `set -e`, any failed command aborts. The script removes any prior temporary `tzdata` directory, recreates it, extracts one timezone file, returns to the backend directory, runs the Go generator, and removes the temporary tree.

## State and Persistence Behavior

It writes a temporary `tzdata/` directory and updates generated source through `generate_tzdata.go`. It does not edit rclone config or runtime state.

## Dependencies and Integration Points

It is referenced by `//go:generate ./update-timezone.sh` in `sharefile.go`. It depends on a Go toolchain, the Go distribution's zoneinfo archive, `unzip`, and the local generator source.

## Risks and Edge Cases

`rm -rf tzdata` is destructive relative to the backend directory and assumes that name is only temporary. Missing `unzip`, a stripped Go installation without zoneinfo, or generator failure leaves no updated embedded asset. It embeds Go's timezone snapshot, not necessarily the host OS snapshot.

## Test Signals

Run through `go generate` in the package and verify `tzdata_vfsdata.go` compiles. Behavioral confirmation comes from ShareFile modtime tests around Eastern time and DST transitions.
