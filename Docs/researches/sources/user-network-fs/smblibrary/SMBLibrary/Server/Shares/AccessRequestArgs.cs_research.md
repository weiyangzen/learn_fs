<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs

## Purpose
Event argument object for share-level access decisions. It carries user, path, requested access, machine, and client endpoint details to `FileSystemShare.AccessRequested` subscribers.

## APIs, Types, and Functions
`AccessRequestArgs` derives from `EventArgs` and exposes public fields `UserName`, `Path`, `RequestedAccess`, `MachineName`, `ClientEndPoint`, and mutable `Allow` defaulting to true. The constructor initializes all request context fields.

## Control Flow, State, and Persistence
There is no control flow beyond construction. The mutable `Allow` field is the event response channel; subscribers set it to deny access. No persistence is used.

## Dependencies and Integration
Created by `FileSystemShare.HasAccess()` and consumed by applications such as `SMBServer.ServerUI.InitializeShare()`.

## Risks and Test Signals
Risks include public mutable fields, default-allow behavior when handlers do not set `Allow`, and coarse `FileAccess` categories. Test event subscribers for read/write/read-write requests, null or wildcard account policies, and propagation of machine/end-point values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs -->
