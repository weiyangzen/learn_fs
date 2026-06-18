<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/nullauthhandler.go -->
# sources/user-network-fs/go-nfs/helpers/nullauthhandler.go

## Purpose
Provides a trivial no-auth handler exposing one billy filesystem for all mount requests.

## Important APIs, Types, and Functions
`NewNullAuthHandler`, `NullAuthHandler.Mount`, `Change`, `FSStat`, handle stubs, and `HandleLimit` are central.

## Control Flow
Mount always succeeds with `AUTH_NULL`; `Change` returns the filesystem if it implements `billy.Change`; handle methods are placeholders intended to be wrapped by `CachingHandler`.

## State and Persistence Behavior
State is only the embedded billy filesystem.

## Dependencies and Integration Points
Used by examples and tests as the simplest `nfs.Handler` implementation.

## Risks and Edge Cases
Using it without `CachingHandler` returns empty handles and cannot resolve them. It performs no authorization or export path checks.

## Test Signals
Examples and helper tests validate it in combination with `CachingHandler`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/nullauthhandler.go -->
