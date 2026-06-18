# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteReader.cs

Purpose: `ByteReader` provides endian-neutral byte, byte-array, ANSI, UTF-16, and null-terminated string reading helpers.

Important APIs/types/functions: `ReadByte`, `ReadBytes`, `ReadAnsiString`, `ReadUTF16String`, null-terminated ANSI/UTF-16 readers for arrays, `ReadBytes(Stream,count)`, `ReadAllBytes(Stream)`, and stream ANSI readers. ANSI uses code page 28591 to preserve byte values better than ASCII replacement.

Control flow: fixed-length methods copy or decode spans and advance `ref` offsets. Null-terminated methods loop until a zero terminator. Stream methods copy to a `MemoryStream` via `ByteUtils.CopyStream`.

State and persistence behavior: stateless, with caller offset mutation and stream position consumption.

Dependencies and integration points: depends on `ByteUtils.CopyStream`, `LittleEndianConverter` for UTF-16 null-terminated array reads, and .NET encodings.

Risks: null-terminated readers can overrun buffers or loop until stream `ReadByte()` returns -1, which becomes a nonzero char, if input is unterminated. No bounds checks precede array access. Stream fixed reads may return fewer bytes if the source ends early.

Test signals: fixed and null-terminated string tests, code page preservation tests for bytes above 0x7f, unterminated input failure behavior, offset advancement, and stream short-read cases.
