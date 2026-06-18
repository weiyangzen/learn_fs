# sources/user-network-fs/impacket/impacket/dcerpc/v5/atsvc.py

## Purpose

`atsvc.py` implements the ATSVC interface for the legacy Task Scheduler service as specified by MS-TSCH. It defines the interface UUID, task/job structures, request/response NDR call classes for job add/delete/enumerate/get-info, opnum mapping, and simple helper functions for issuing those calls.

## Important APIs, Types, and Functions

`MSRPC_UUID_ATSVC` identifies the interface. `DCERPCSessionError` formats HRESULT errors through `hresult_errors`. Constants include ATSVC name-length and task flag values. NDR structures include `AT_INFO`, `LPAT_INFO`, `AT_ENUM`, `AT_ENUM_ARRAY`, `LPAT_ENUM_ARRAY`, and `AT_ENUM_CONTAINER`.

RPC classes are `NetrJobAdd`, `NetrJobAddResponse`, `NetrJobDel`, `NetrJobDelResponse`, `NetrJobEnum`, `NetrJobEnumResponse`, `NetrJobGetInfo`, and `NetrJobGetInfoResponse`. `OPNUMS` maps opnums 0 through 3 to request/response classes. Helpers `hNetrJobAdd`, `hNetrJobDel`, `hNetrJobEnum`, and `hNetrJobGetInfo` populate request objects and call `dce.request`.

## Control Flow

Callers bind a DCE/RPC connection to `MSRPC_UUID_ATSVC`, then either instantiate request classes directly or use helper functions. Helpers fill server name, job IDs, enum containers, resume handles, and `AT_INFO` payloads before sending. Responses carry returned job IDs, containers, resume handles, and `ErrorCode` fields.

## State and Persistence Behavior

The module itself is stateless. Remote persistence is server-side: `NetrJobAdd` creates scheduled jobs and `NetrJobDel` removes them on the target scheduler service. Local request objects are temporary NDR serialization containers.

## Dependencies and Integration Points

It depends on Impacket's NDR base classes, DCE/RPC data types, UUID conversion, `hresult_errors`, and `DCERPCException`. It integrates with `impacket.dcerpc.v5.transport` and `rpcrt` connections and with SMB/RPC test cases under Impacket's SMB_RPC suite.

## Risks and Edge Cases

The helper `hNetrJobEnum` only sets `pEnumContainer['Buffer']` and does not expose a resume handle parameter, even though the request structure includes one. Callers must build valid `AT_INFO` scheduling fields themselves; this file does not validate time, day, flag, or command semantics. Creating or deleting jobs is security-sensitive and depends on remote privileges.

## Test Signals

Unit tests can verify NDR field layout and helper request fields. Integration tests should bind to ATSVC on a controlled Windows target or mock DCE transport, add a harmless job, enumerate it, retrieve it, delete it, and validate formatted errors for known HRESULT values.
