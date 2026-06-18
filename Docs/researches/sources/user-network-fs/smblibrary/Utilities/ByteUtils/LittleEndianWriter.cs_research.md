# sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianWriter.cs

Purpose: `LittleEndianWriter` serializes integer and GUID values to byte arrays or streams in little-endian order.

Important APIs/types/functions: buffer/ref-offset/stream overloads for 16-, 32-, and 64-bit signed and unsigned integers, plus GUID buffer writers.

Control flow: delegates byte generation to `LittleEndianConverter`, copies/writes the bytes, and advances ref offsets by the field width.

State and persistence behavior: stateless except for target mutation and offset advancement.

Dependencies and integration points: pairs with `LittleEndianReader` and is a basic serializer for SMB binary structures.

Risks: no explicit capacity checks. Stream overload set lacks `WriteGuid(Stream, Guid)`, unlike the big-endian writer. Errors are runtime exceptions from the target.

Test signals: round-trip tests for each width, GUID buffer layout, offset movement, and consistency with `BitConverter` on little-endian hosts.
