# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorystream.h

Purpose: `MemoryStream` adapts a caller-provided byte buffer and explicit size to RapidJSON's input stream concept.

Important APIs and types: The struct exposes `Ch = char`, constructor `MemoryStream(const Ch* src, size_t size)`, `Peek()`, `Take()`, `Tell()`, `Peek4()`, and public fields `src_`, `begin_`, `end_`, and `size_`. Output stream methods assert if called.

Control flow: `Peek()` returns the current byte or `'\0'` at end. `Take()` returns the current byte and advances unless already at end, where it returns `'\0'`. `Tell()` is pointer subtraction from the beginning. `Peek4()` returns the current pointer only when at least four bytes remain.

State and persistence behavior: The stream does not own the buffer. State is the current pointer and bounds. It reads from memory only and persists nothing.

Dependencies and integration points: It includes `stream.h`. It is useful for `EncodedInputStream` and `AutoUTFInputStream` because it supports `Peek4()` while unlike `StringStream` it does not require null termination or an encoding.

Risks: Caller must keep the source buffer alive. `'\0'` can be a valid byte inside the buffer but also marks end for stream concept consumers, so byte-level wrappers must honor size and parser expectations. Public fields can be mutated by callers.

Test signals: Cover empty buffers, buffers containing null bytes, exact end behavior, `Tell()` after reads, `Peek4()` at offsets with three/four bytes remaining, and parsing non-null-terminated JSON data.
