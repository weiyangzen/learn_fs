<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs

## Purpose
Reads little-endian NDR primitives, strings, structures, top-level full pointers, and embedded deferred referents.

## Important APIs, Types, And Functions
Declarations: `public class NDRParser`. Serialization surface: buffer constructors/read methods. Specific behavior: it tracks offset alignment, structure nesting depth, deferred structures, and referent id reuse.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is transient parser/writer offset or stream position, structure nesting depth, deferred referent list, and referent-id map. It persists only for one NDR stub encode/decode operation.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs -->
