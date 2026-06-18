# sources/object-store/minio-mc/cmd/client-fs_darwin.go

## Purpose

This Darwin-specific companion supplies macOS filesystem event classification and xattr readers used by `client-fs.go`. It is selected by the `darwin` build tag and keeps platform-specific notify/xattr behavior out of the portable filesystem client.

## Important APIs, Control Flow, And State

The file defines `EventTypePut` as create/write/rename, `EventTypeDelete` as remove, and `EventTypeGet` as empty because access/read notifications are not available for this backend. `IsPutEvent` tests bit overlap against the put event list, `IsDeleteEvent` checks `notify.Remove`, and `IsGetEvent` always returns false. `getXAttr` wraps `xattr.Get`, while `getAllXattrs` lists all extended attribute keys, reads each value, and treats filesystem-not-supported errors from `isNotSupported` as a nil metadata result rather than a hard failure.

## Dependencies, Integration, Risks, And Tests

Dependencies are `github.com/rjeczalik/notify` and `github.com/pkg/xattr`. The functions are consumed by preserve-mode `Get`/`Stat` and by `Watch` in `client-fs.go`. The main risk is silent loss of get events on macOS, which is explicit, and xattr read failures after a successful list. Tests are mostly indirect through filesystem preserve/list/watch behavior; `client-fs_test.go` has OS-specific assertions for `.DS_Store` filtering on Darwin.
