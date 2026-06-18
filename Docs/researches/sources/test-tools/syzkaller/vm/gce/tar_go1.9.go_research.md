# sources/test-tools/syzkaller/vm/gce/tar_go1.9.go

## Purpose

`tar_go1.9.go` provides a pre-Go-1.10 fallback for forcing GNU tar format in GCE image uploads.

## Important APIs, Types, and Functions

It defines `setGNUFormat(hdr *tar.Header)`, assigning large `Uid` and `Gid` values to force the older `archive/tar` package to select GNU format.

## Control Flow

The build tag selects this file when Go 1.10 APIs are unavailable. `uploadImageToGCS` calls the same function name and receives GNU-compatible tar output indirectly.

## State and Persistence Behavior

Only the tar header is mutated. The resulting tar stream contains synthetic large owner IDs used solely as a format-selection hack.

## Dependencies and Integration Points

It depends on `archive/tar` behavior in old Go releases and GCE's expectation for old GNU tar format.

## Risks and Test Signals

This is intentionally hacky and relies on historical standard-library behavior. Tests on old toolchains should verify GCE accepts generated archives and that the `disk.raw` member remains readable.
