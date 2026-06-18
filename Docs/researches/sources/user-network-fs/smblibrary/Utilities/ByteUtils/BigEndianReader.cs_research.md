# sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianReader.cs

Purpose: `BigEndianReader` reads primitive numeric and GUID values from byte arrays or streams in network byte order.

Important APIs/types/functions: array readers for `Int16`, `UInt16`, 24-bit unsigned integer, `Int32`, `UInt32`, `Int64`, `UInt64`, and `Guid`; stream readers for the same except 24-bit uses a padded 4-byte buffer. `ref int offset` overloads advance the caller's cursor.

Control flow: each `ref` overload increments offset by the field width and calls `BigEndianConverter` at the prior offset. Stream overloads allocate fixed-size buffers and perform one `Read`.

State and persistence behavior: stateless utility; the only state mutation is the caller-provided offset.

Dependencies and integration points: depends on `BigEndianConverter` and `System.IO.Stream`. It pairs with `BigEndianWriter` for protocol serialization.

Risks: stream `Read` return values are ignored, so short reads produce partially zero-filled conversions rather than an error. Array overloads rely on runtime bounds exceptions. 24-bit conversion uses byte shifts promoted to signed `int`, but byte inputs remain safe for the target width.

Test signals: round-trip tests with `BigEndianWriter`, offset advancement tests, boundary buffer tests, and short stream read tests are the key coverage signals.
