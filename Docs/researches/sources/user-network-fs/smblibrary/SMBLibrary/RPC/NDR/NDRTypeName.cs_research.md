<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs

## Purpose
Names supported NDR primitive/constructed helper types.

## Important APIs, Types, And Functions
Declarations: `public enum NDRTypeName`. Enum values include `{`, `UnicodeString`. Specific behavior: it currently contains UnicodeString as the only type marker.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs -->
