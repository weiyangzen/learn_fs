# sources/user-network-fs/impacket/impacket/dcerpc/v5/srvs.py

## Purpose

`srvs.py` implements Impacket's [MS-SRVS] Server Service RPC interface binding metadata. It is a protocol-schema module: it defines the SRVS UUID, constants, NDR structure/union/pointer classes for server/share/session/file/transport/DFS data, NDR call classes for supported opnums, the `OPNUMS` dispatch table, and helper functions that populate request objects and send them through an existing DCE/RPC connection.

The file does not open sockets or authenticate by itself. Callers are expected to build a DCE/RPC transport elsewhere, bind to `MSRPC_UUID_SRVS`, and then call helpers such as `hNetrShareEnum`, `hNetrServerGetInfo`, or `hNetrpGetFileSecurity`.

## Important APIs, types, and functions

- `MSRPC_UUID_SRVS` identifies the Server Service interface version 3.0.
- `DCERPCSessionError` renders SRVS RPC failures using `impacket.system_errors.ERROR_MESSAGES`.
- Constants cover share types (`STYPE_*`), session flags, platform/server type flags, path and name validation types, DFS flags, parameter-error codes, and `MAX_PREFERRED_LENGTH`.
- Core NDR data families include `CONNECTION_INFO_*`, `FILE_INFO_*`, `SESSION_INFO_*`, `SHARE_INFO_*`, `SERVER_INFO_*`, `DISK_INFO`, `SERVER_TRANSPORT_INFO_*`, `SERVER_ALIAS_INFO_*`, `TIME_OF_DAY_INFO`, security descriptor wrappers, and DFS entry/site structs.
- Union/container classes are the important level selectors: `CONNECT_ENUM_UNION`, `FILE_ENUM_UNION`, `SESSION_ENUM_UNION`, `SHARE_ENUM_UNION`, `SERVER_INFO`, `TRANSPORT_INFO`, and `SERVER_ALIAS_INFO`.
- RPC call classes model opnums 8 through 57, including connection/file/session enumeration, share add/enum/get/set/delete, server get/set/disk/statistics/time, transport add/enum/delete, path/name canonicalization and comparison, DFS management, server alias management, and extended share deletion.
- `OPNUMS` maps each supported opnum to request/response classes for `rpcrt` unmarshalling.
- Helper functions prefixed `h` create requests and call `dce.request()`. Notable helpers include `hNetrShareEnum`, `hNetrShareAdd`, `hNetrShareSetInfo`, `hNetrServerTransportEnum`, `hNetrpGetFileSecurity`, `hNetrpSetFileSecurity`, and path/name validation helpers.

## Control flow

Import-time execution defines constants and classes only. Runtime flow is thin:

1. A caller creates or receives a bound DCE/RPC object.
2. A helper allocates the corresponding `NDRCALL` request.
3. The helper fills `ServerName`, level fields, union tags, buffers, resume handles, and payload structures.
4. `dce.request(request)` serializes the NDR request, invokes the remote opnum, and unmarshals the response through `OPNUMS`.

The main control-flow risk is correct union tagging. Enumeration helpers explicitly set both the outer `Level` and inner union `tag`, and set returned array buffers to `NULL` before the call. Add/set helpers assign the correct `ShareInfo%d`, `ServerAliasInfo%d`, or related level-specific arm.

## State and persistence behavior

The module is stateless aside from class definitions and constants. Persistent effects happen on the remote server, not locally:

- Share helpers can add, update, delete, or perform staged deletion of server shares.
- Server-set and transport add/delete calls can alter server configuration.
- DFS helpers can create/delete partitions, change local volume state, and create/delete exit points.
- File-security helpers read or write remote share-relative security descriptors.

Local helper state is limited to request objects and resume handles. The caller owns pagination loops via `ResumeHandle` and `PreferedMaximumLength`.

## Dependencies and integration points

- Depends on `impacket.dcerpc.v5.ndr` for NDR base classes, arrays, unions, and pointers.
- Depends on `impacket.dcerpc.v5.dtypes` for common Windows/RPC scalar and string types.
- Uses `impacket.dcerpc.v5.rpcrt.DCERPCException` for session errors.
- Uses `impacket.uuid.uuidtup_to_bin` for UUID encoding.
- Integrates with transport and RPC binding code outside this file; common use is over SMB named pipe transports against `\pipe\srvsvc`.
- The header points users to Impacket SMB_RPC tests as usage examples.

## Risks and implementation notes

- Several helpers do not normalize trailing NULs consistently. `hNetrShareEnum` enforces a final NUL for `serverName`, while many other `WSTR`/`LPWSTR` inputs are passed through as provided.
- Level/tag mismatches in caller-provided `infoStruct` or `shareInfo` objects can produce malformed NDR requests or server-side `ERROR_INVALID_LEVEL`/parameter errors.
- `SHARE_INFO_1005_ARRAY.item` is set to `SHARE_INFO_1004`, which looks like a likely copy/paste defect for level 1005 array handling.
- Security descriptor helpers manually convert buffers: `hNetrpGetFileSecurity` joins returned descriptor bytes, and `hNetrpSetFileSecurity` sets length plus byte-list buffer. Tests should cover binary descriptor round trips.
- Destructive administrative calls are exposed without guardrails. Higher-level tools must enforce authorization checks, dry-run behavior, and user confirmation if needed.
- Many NDR schemas mirror protocol documents and are not locally validated beyond Impacket serialization.

## Test signals

Useful tests should bind to an SRVS-capable endpoint and cover:

- Share enumeration at levels 0, 1, 2, 501, 502, and 503, including resume-handle pagination.
- Share add/get/set/delete for level-specific structures and `ParmErr` behavior.
- Session, file, connection, disk, transport, server alias, path/name, and remote time helpers.
- Security descriptor get/set byte preservation.
- Error formatting through `DCERPCSessionError` for known and unknown system error codes.
- Regression tests for union tag setup and the suspicious `SHARE_INFO_1005_ARRAY` item type.
