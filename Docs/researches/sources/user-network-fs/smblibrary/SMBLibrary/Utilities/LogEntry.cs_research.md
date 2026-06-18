<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs

## Purpose
Shared logging event payload and severity enumeration used by the SMB server and sample application.

## APIs, Types, and Functions
`Severity` enum ranges from `Critical` to `Trace`. `LogEntry : EventArgs` exposes public fields `Time`, `Severity`, `Source`, and `Message`, initialized by constructor.

## Control Flow, State, and Persistence
No logic beyond construction. Persistence occurs only when subscribers such as `LogWriter` write entries.

## Dependencies and Integration
Used by `SMBServer.LogEntryAdded`, connection logging, and `SMBServer/LogWriter.cs`.

## Risks and Test Signals
Risks include public mutable fields and no structured event IDs. Test event delivery, severity filtering, and timestamp/source propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs -->
