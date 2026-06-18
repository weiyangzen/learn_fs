# sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianWriter.cs

Purpose: `BigEndianWriter` serializes primitive numeric and GUID values to byte arrays or streams in big-endian order.

Important APIs/types/functions: `WriteInt16`, `WriteUInt16`, `WriteUInt24`, `WriteInt32`, `WriteUInt32`, `WriteInt64`, `WriteUInt64`, and `WriteGuid`; overloads write to buffer offsets, advance `ref int offset`, or write directly to a `Stream`.

Control flow: methods obtain bytes from `BigEndianConverter`, copy or write the relevant bytes, and advance offsets by fixed field sizes. UInt24 writes bytes 1..3 of a 32-bit big-endian representation.

State and persistence behavior: stateless except for mutating the target buffer/stream and offset.

Dependencies and integration points: pairs with `BigEndianReader` and `BigEndianConverter`, used wherever wire formats require network byte order.

Risks: no buffer capacity checks beyond `Array.Copy` exceptions. Stream writes assume the stream accepts the entire buffer. UInt24 silently truncates values above 24 bits.

Test signals: round trips for all widths, explicit byte-order assertions, offset movement, UInt24 truncation/bounds behavior, and GUID byte layout tests.
