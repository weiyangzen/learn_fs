# Research: sources/user-network-fs/rclone/backend/azureblob/azureblob_unsupported.go

## Purpose
This platform stub prevents Go from reporting "no buildable Go source files" for the `azureblob` package on unsupported targets. The real backend is excluded on `plan9`, `solaris`, and `js`; this file keeps the package present there.

## Important APIs, Types, and Functions
The file declares only package `azureblob` under build tag `plan9 || solaris || js`. It exports no types, functions, variables, or registration hooks.

## Control Flow
There is no runtime control flow. Build constraints select this file only where `azureblob.go` is not compiled.

## State and Persistence Behavior
No state is held and no persistence occurs.

## Dependencies and Integration Points
The only integration point is Go's build system. On unsupported platforms the backend has no implementation and no `fs.Register` call from this package.

## Risks and Edge Cases
Code importing platform-specific backend symbols will not find them on these targets unless guarded by matching build tags. This is intentional because the Azure SDK/backend implementation is not available there.

## Test Signals
There are no tests for this stub. Successful package loading/building on unsupported targets is the only signal.
