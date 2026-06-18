# sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianReader.cs

Purpose: `LittleEndianReader` reads little-endian primitive integers and GUIDs from arrays and streams.

Important APIs/types/functions: array and stream readers for `Int16`, `UInt16`, `Int32`, `UInt32`, `Int64`, `UInt64`, and `Guid`, with `ref int offset` cursor advancement for arrays.

Control flow: methods advance offsets by fixed widths and delegate conversion to `LittleEndianConverter`; stream methods allocate exact-width buffers and read once.

State and persistence behavior: stateless apart from caller offset and stream position.

Dependencies and integration points: pairs with `LittleEndianWriter` and `LittleEndianConverter`; used for SMB-related binary layouts that are little-endian.

Risks: stream short reads are not detected. Array bounds errors are left to runtime exceptions. No float stream helpers despite converter support.

Test signals: endian byte-order assertions, writer round trips, offset advancement, GUID layout tests, and short stream behavior.
