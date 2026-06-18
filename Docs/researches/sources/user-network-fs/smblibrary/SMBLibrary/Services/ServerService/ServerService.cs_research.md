<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs

## Purpose
Implementation of the `srvsvc` named-pipe RPC service subset. It supports share enumeration, share get-info, and server get-info responses for SMB clients browsing shares through `IPC$`.

## APIs, Types, and Functions
`ServerService : RemoteService` exposes constants for pipe name, interface GUID, version, and max preferred length. It implements `GetResponseBytes()`, `GetNetrShareEnumResponse()`, `GetNetrShareGetInfoResponse()`, `GetNetrWkstaGetInfoResponse()` for server info, `IndexOfShare()`, `InterfaceGuid`, and `PipeName`.

## Control Flow, State, and Persistence
Constructor stores platform/server/version/type values and an in-memory share list. Dispatch switches on `ServerServiceOpName`, parses request bytes, and serializes responses. Share enum supports levels 0 and 1, rejects levels 2/501/502/503 as not supported, and invalid levels as invalid. Share get-info supports levels 0, 1, and 2. Server get-info supports 100 and 101. State is fixed after construction.

## Dependencies and Integration
Instantiated by `NamedPipeShare`; called through RPC pipe framing. Depends on NDR request/response structures, share/server info structures, `Win32Error`, and `UnsupportedOpNumException`.

## Risks and Test Signals
Risks include stale share list, no paging/resume support, limited levels, method naming typo, level/union inconsistencies in `ShareInfo.Read()`, and hard-coded Windows version/type identity. Test Windows share browsing, `net view`, level 0/1/2 get-info, unsupported opnums, invalid levels, and empty share lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs -->
