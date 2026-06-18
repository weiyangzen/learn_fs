<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs

## Purpose
Packs NetBIOS name-service owner node type and group/workgroup bit into the two-byte name flags field.

## Important APIs, Types, And Functions
Declarations: `public enum OwnerNodeType : byte`; `public struct NameFlags`. Constants: `public const int Length = 2;`. Important fields include `public OwnerNodeType NodeType`, `public bool WorkGroup`. Enum values include `{`, `BNode = 0x00`, `PNode = 0x01`, `MNode = 0x10`. Specific behavior: it implements explicit conversions to and from ushort for resource-record data.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs -->
