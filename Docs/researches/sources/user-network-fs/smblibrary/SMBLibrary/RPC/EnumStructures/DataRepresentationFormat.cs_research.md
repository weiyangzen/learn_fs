<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs

## Purpose
Models the DCE/RPC packed data representation label for character set, byte order, and floating-point representation.

## Important APIs, Types, And Functions
Declarations: `public enum CharacterFormat : byte`; `public enum ByteOrder : byte`; `public enum FloatingPointRepresentation : byte`; `public struct DataRepresentationFormat`. Important fields include `public CharacterFormat CharacterFormat`, `public ByteOrder ByteOrder`, `public FloatingPointRepresentation FloatingPointRepresentation`. Enum values include `{`, `ASCII = 0x00`, `EBCDIC = 0x01`, `{`, `BigEndian = 0x00`, `LittleEndian = 0x01`, `{`, `IEEE = 0x00`, `VAX = 0x01`, `Cray = 0x02`, `IBM = 0x03`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it packs character format in the low nibble and byte order in the high nibble of the first byte.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs -->
