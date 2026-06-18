# sources/user-network-fs/rclone/lib/diskusage/diskusage_unsupported.go

## Purpose
This file provides the `diskusage.New` implementation for platforms where disk usage is unsupported.

## Important APIs, types, and functions
- Build constraint: `illumos || js || plan9 || solaris`.
- `New(dir string) (Info, error)` returns zero `Info` and `ErrUnsupported`.

## Control flow
The function immediately returns without inspecting `dir`.

## State and persistence behavior
No state is read or changed.

## Dependencies and integration points
It depends only on shared package symbols. Callers and tests can branch on `ErrUnsupported`.

## Risks and edge cases
Callers must handle unsupported platforms gracefully. The function does not validate paths because no platform syscall is attempted.

## Test signals
`diskusage_test.go` skips when this implementation returns `ErrUnsupported`.
