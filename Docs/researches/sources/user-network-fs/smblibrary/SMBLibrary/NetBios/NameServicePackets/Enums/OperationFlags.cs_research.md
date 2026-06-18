<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs

## Purpose
Defines protocol constants for `OperationFlags` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum OperationFlags : byte`. Enum values include `{`, `Broadcast = 0x01`, `RecursionAvailable = 0x08`, `RecursionDesired = 0x10`, `Truncated = 0x20`, `AuthoritativeAnswer = 0x40`.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs -->
