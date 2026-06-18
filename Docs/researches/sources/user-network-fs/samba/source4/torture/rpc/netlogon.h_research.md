# sources/user-network-fs/samba/source4/torture/rpc/netlogon.h

## Purpose

`netlogon.h` is a small local header that exposes selected Netlogon torture helper functions implemented in `netlogon.c` for reuse by sibling RPC torture files. It avoids duplicating the secure-channel bootstrap logic in tests that need authenticated Netlogon state.

## Important APIs, Types, and Functions

The header declares:

- `test_SetupCredentials2()`: authenticate using `ServerAuthenticate2` with caller-supplied negotiate flags and secure-channel type.
- `test_SetupCredentials3()`: authenticate using `ServerAuthenticate3` with caller-supplied negotiate flags.
- `test_SetupCredentialsPipe()`: open a second DCERPC pipe using existing Netlogon credential state and additional DCERPC auth options.

The declarations use `struct dcerpc_pipe`, `struct torture_context`, `struct cli_credentials`, and `struct netlogon_creds_CredentialState`. The secure-channel argument in `test_SetupCredentials2()` is an `int` in the header, while the implementation uses `enum netr_SchannelType`; callers should pass the enum-compatible values from Samba credential helpers.

## Control Flow

The header has no runtime control flow. Its role is compile-time linkage: consumers include it, call a setup helper to establish credential state, then optionally call `test_SetupCredentialsPipe()` to get a schannel-protected pipe for subsequent RPC operations.

## State and Persistence Behavior

No state is stored in the header. The declared functions operate on caller-owned pipes and credentials. `test_SetupCredentialsPipe()` is stateful through `cli_credentials_set_netlogon_creds()` in the implementation, but the header itself only exposes the contract.

## Dependencies and Integration Points

The file assumes the including translation unit already has compatible Samba type declarations available. It integrates Netlogon helper routines across the `source4/torture/rpc` test area.

## Risks and Edge Cases

The declarations are not protected by an include guard in this file. In practice it is small and likely included once, but adding another include path could cause repeated declaration warnings only if signatures drift. The `int` versus enum secure-channel parameter should be kept ABI-compatible with the implementation.

## Test Signals

There are no standalone tests for this header. Its health is signaled by successful compilation of consumers and by runtime success of tests that use the declared helpers to establish Netlogon credential chains and schannel pipes.
