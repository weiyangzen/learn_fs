# Research: sources/user-network-fs/rclone/backend/azurefiles/azurefiles_unsupported.go

## Purpose
This platform stub keeps the `azurefiles` package buildable on unsupported targets where the real backend is excluded.

## Important APIs, Types, and Functions
The file declares package `azurefiles` under build tag `plan9 || js` and exports no implementation.

## Control Flow
There is no runtime control flow. The Go build system selects this file for unsupported platforms.

## State and Persistence Behavior
No state or persistence behavior exists.

## Dependencies and Integration Points
The only dependency is build-tag selection. Since the implementation file is not compiled, the backend is not registered on these platforms.

## Risks and Edge Cases
Code expecting Azure Files backend symbols must be guarded for these platforms. This is intentional package hygiene rather than functional backend behavior.

## Test Signals
There are no direct tests; successful package loading/building on unsupported targets is the signal.
