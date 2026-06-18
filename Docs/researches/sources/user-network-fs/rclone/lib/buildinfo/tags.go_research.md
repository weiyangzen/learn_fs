# sources/user-network-fs/rclone/lib/buildinfo/tags.go

## Purpose
This file owns build-tag reporting for rclone. It stores tags discovered by build-specific files and converts them into a displayable linking mode plus tag string.

## Important APIs, types, and functions
- `var Tags []string` is the mutable package-level registry populated by init functions in this and other packages/files.
- `GetLinkingAndTags() (linking, tagString string)` returns `"static"` or `"dynamic"` and a sorted tag list or `"none"`.

## Control flow
`GetLinkingAndTags` assumes static linking, walks `Tags`, treats the special tag `"cgo"` as evidence of dynamic linking, and excludes it from the displayed tag list. All remaining tags are sorted and joined by spaces; an empty list is represented as `"none"`.

## State and persistence behavior
`Tags` is process-global mutable state. It is initialized during package startup and then read without locking, so callers assume tag mutation only happens at init time.

## Dependencies and integration points
It depends only on `sort` and `strings`, but is extended by build-tag files such as `snap.go` and comments note `cmd/cmount/mount.go` and `cmd/selfupdate/noselfupdate.go` also append tags.

## Risks and edge cases
Late mutation of `Tags` would race with readers because no mutex is used. Unknown tags are displayed as-is, and duplicate tags are not deduplicated. The `"cgo"` tag has semantic meaning beyond display, so producers must use that exact spelling.

## Test signals
No tests in this subset directly exercise tag formatting. Any version/build-info tests should verify sorted output and cgo handling.
