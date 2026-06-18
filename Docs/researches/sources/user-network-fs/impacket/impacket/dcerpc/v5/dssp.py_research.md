# sources/user-network-fs/impacket/impacket/dcerpc/v5/dssp.py

## Purpose

`dssp.py` implements Impacket's binding for [MS-DSSP], the Directory Services Setup Remote Protocol. Its focused purpose is to query a Windows machine's primary domain role, upgrade state, or operation state through `DsRolerGetPrimaryDomainInformation`.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_DSSP`, `DCERPCSessionError`, domain role flags, and upgrade status constants. The type model includes `DSROLE_MACHINE_ROLE`, `DSROLER_PRIMARY_DOMAIN_INFO_BASIC`, `DSROLE_OPERATION_STATE`, `DSROLE_OPERATION_STATE_INFO`, `DSROLE_SERVER_STATE`, `DSROLE_UPGRADE_STATUS_INFO`, `DSROLE_PRIMARY_DOMAIN_INFO_LEVEL`, and the union `DSROLER_PRIMARY_DOMAIN_INFORMATION`.

The only RPC method modeled is `DsRolerGetPrimaryDomainInformation` at opnum 0, with `DsRolerGetPrimaryDomainInformationResponse`. `OPNUMS` maps opnum 0, and `hDsRolerGetPrimaryDomainInformation(dce, infoLevel)` is the single helper.

## Control Flow

The helper creates a request, assigns `InfoLevel`, and delegates to `dce.request()`. The NDR layer handles the returned union according to `DSROLE_PRIMARY_DOMAIN_INFO_LEVEL`. Error formatting checks `system_errors.ERROR_MESSAGES` and emits DSSP-specific session error text.

## State And Persistence Behavior

There is no local persistence or mutable module state. All state is transient in request/response objects and in the remote server configuration being queried. The implemented call is read-only and does not modify the remote machine.

## Dependencies And Integration Points

Dependencies are `rpcrt.DCERPCException`, NDR classes, common dtypes (`UINT`, `LPWSTR`, `GUID`), `system_errors`, the local `Enum`, and UUID helpers. The module integrates with a DCE connection bound to the DSSP interface and is useful for host profiling tools that need workstation/server/domain-controller role information.

## Risks And Edge Cases

Protocol coverage is narrow: only opnum 0 is implemented. Invalid info levels may fail server-side or during local union decoding. Error formatting only checks system errors, so HRESULT-style failures may be reported as unknown.

## Test Signals

Tests should verify that each info level selects the expected union arm, that the helper sends opnum 0 with the requested level, and that basic domain info serializes nullable/non-null `LPWSTR` fields correctly. Integration tests can compare results with known member-server and domain-controller fixtures.
