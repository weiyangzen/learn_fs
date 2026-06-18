# sources/user-network-fs/samba/source3/librpc/idl/libnetapi.idl

## Purpose
`libnetapi.idl` declares Samba's local NetAPI-compatible interface. It defines Windows-style status codes, flags, structs, and `nopush,nopull` function prototypes for domain join, server/workstation info, DC discovery, user/group/local-group management, share/file APIs, shutdown, and netlogon control.

## Important APIs, types, and functions
- `NET_API_STATUS` includes success and offline-domain-join error codes.
- `domsid` is a public fixed-size SID representation for API consumers.
- Domain APIs include `NetJoinDomain`, `NetUnjoinDomain`, `NetGetJoinInformation`, `NetGetJoinableOUs`, `NetRenameMachineInDomain`, `NetProvisionComputerAccount`, `NetRequestOfflineDomainJoin`, and `NetComposeOfflineDomainJoin`.
- Server/workstation/DC APIs include `NetServerGetInfo`, `NetServerSetInfo`, `NetWkstaGetInfo`, `NetGetDCName`, `NetGetAnyDCName`, and `DsGetDcName`.
- Account APIs define many `USER_INFO_*`, `GROUP_INFO_*`, `LOCALGROUP_*`, display, modal, SID name-use, and membership structures.
- Share/file/admin APIs include `NetShare*`, `NetFile*`, `NetRemoteTOD`, `NetShutdown*`, `I_NetLogonControl`, and `I_NetLogonControl2`.

## Control flow
The IDL itself does not implement operations. Function declarations use `nopush,nopull`, so generated code primarily provides type definitions and prototypes for local implementations. Many APIs use level numbers plus `uint8 *buffer`/`uint8 **buffer`, mirroring Windows NetAPI conventions where the implementation interprets the buffer according to level.

## State and persistence behavior
The declared APIs can mutate persistent domain membership, machine account state, local SAM users/groups, shares, server parameters, and shutdown state. Resume handles and preferred maximum lengths model paged enumeration state. Password fields and encrypted password arrays appear in user and join structures, so callers must manage sensitive data carefully.

## Dependencies and integration points
The file imports `misc.idl`, emits C preprocessor helper definitions, and is built into `NDR_LIBNETAPI` with `SKIP_NDR_TABLE_libnetapi`. It integrates with libnetapi implementations, libnet join code, SAMR/LSA/netlogon plumbing, share management, and Windows-compatible administrative tools.

## Risks and edge cases
Level-dispatched `uint8 *` buffers are prone to mismatched casts, missing validation, and incomplete parameter-error reporting. Numerous legacy levels and constants need Windows compatibility. Some declarations show naming inconsistencies in late server-info levels, so generated field names must be checked against implementation expectations. Secret fields are plain strings in the local API and require caller-side redaction/zeroing.

## Test signals
Compatibility tests should cover each supported info level, invalid level handling, parameter error indexes, paged enumeration/resume behavior, local vs remote server dispatch, join/offline-join error codes, user/group/share create/update/delete flows, and ABI/header generation for consumers.
