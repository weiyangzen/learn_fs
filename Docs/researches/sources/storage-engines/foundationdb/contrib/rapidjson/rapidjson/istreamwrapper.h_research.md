# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/istreamwrapper.h

Purpose: `BasicIStreamWrapper` adapts `std::basic_istream`-derived objects to RapidJSON's input stream concept.

Important APIs and types: `BasicIStreamWrapper<StreamType>` exposes `Ch`, constructor from a stream reference, `Peek()`, `Take()`, `Tell()`, and `Peek4()` for byte-stream encoding detection. Typedefs `IStreamWrapper` and `WIStreamWrapper` cover `std::istream` and `std::wistream`.

Control flow: `Peek()` delegates to `stream_.peek()` and returns `'\0'` on EOF. `Take()` calls `stream_.get()`, increments an internal count only on successful reads, and returns `'\0'` on EOF. `Tell()` returns this count instead of `tellg()` because `tellg()` can fail. `Peek4()` temporarily reads up to four bytes, stores them in a mutable buffer, clears EOF state if needed, puts bytes back in reverse order, and returns null if fewer than four are available.

State and persistence behavior: The wrapper holds a reference to the stream, a read count, and a mutable four-character peek buffer. It does not own or close the stream.

Dependencies and integration points: It includes `stream.h` and `<iosfwd>`. It lets document/reader parsing operate on C++ streams without copying into memory first.

Risks: `Peek4()` asserts one-byte `Ch`, so it is not for wide streams. Putback may fail on unusual stream buffers. The count can diverge from external stream repositioning because the wrapper assumes sequential reads.

Test signals: Parse from string streams and file streams, verify `Tell()` after reads and EOF, exercise `Peek4()` success/failure and putback preservation, wide-stream basic parsing, and behavior with externally manipulated streams.
