<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs

## Purpose
Implementation of the `wkssvc` named-pipe RPC service subset, supporting workstation get-info responses for SMB clients querying host/workgroup metadata.

## APIs, Types, and Functions
`WorkstationService : RemoteService` exposes pipe name, interface GUID, version, constructor, `GetResponseBytes()`, `GetNetrWkstaGetInfoResponse()`, and overrides for `InterfaceGuid` and `PipeName`.

## Control Flow, State, and Persistence
Constructor stores platform ID, computer name, LAN group, and hard-coded major/minor version. Dispatch implements only `NetrWkstaGetInfo`; other opnums throw `UnsupportedOpNumException`. Level 100 and 101 return populated info structures; levels 102 and 502 return not-supported; others return invalid-level. State is fixed per service instance.

## Dependencies and Integration
Created by `NamedPipeShare` and invoked through `RPCPipeStream`. Uses workstation request/response and info structures, `Win32Error`, and `PlatformName`.

## Risks and Test Signals
Risks include limited opnum and level support, hard-coded version values, `LanRoot` value choice, and no dynamic domain/workgroup discovery. Test `wkssvc` bind, level 100/101 get-info, unsupported levels, invalid levels, and unsupported opnums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs -->
