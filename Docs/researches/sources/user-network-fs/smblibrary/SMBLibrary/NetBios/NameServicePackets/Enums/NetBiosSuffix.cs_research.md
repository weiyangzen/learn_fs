<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs

## Purpose
Defines protocol constants for `NetBiosSuffix` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum NetBiosSuffix : byte`. Enum values include `{`, `WorkstationService = 0x00`, `MessengerService = 0x03`, `DomainMasterBrowser = 0x1B`, `MasterBrowser = 0x1D`, `BrowserServiceElections = 0x1E`, `FileServerService = 0x20`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs -->
