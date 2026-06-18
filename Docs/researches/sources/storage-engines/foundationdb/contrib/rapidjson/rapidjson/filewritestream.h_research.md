# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filewritestream.h

Purpose: `FileWriteStream` adapts a `std::FILE*` plus caller-owned buffer to RapidJSON's output stream concept for byte-oriented JSON writing.

Important APIs and types: The class exposes `typedef char Ch`, constructor `FileWriteStream(std::FILE*, char*, size_t)`, `Put(char)`, `PutN(char, size_t)`, and `Flush()`. A specialized free `PutN(FileWriteStream&, char, size_t)` delegates to the efficient member implementation.

Control flow: `Put()` flushes when the buffer is full and writes one byte into the buffer. `PutN()` fills the available buffer with `memset`, flushing as many complete chunks as necessary, then stores any remainder. `Flush()` writes buffered bytes with `fwrite()` and resets `current_` to the buffer start.

State and persistence behavior: The stream holds raw pointers to the file and buffer and tracks `bufferEnd_` and `current_`. It writes to the file but does not own or close it. Write failures are deliberately ignored except for avoiding unused-result warnings, so no sticky error state is exposed.

Dependencies and integration points: It includes `stream.h` and `<cstdio>`. `Writer`, `PrettyWriter`, and encoded output streams can use it as a sink. The generic `PutN` specialization is used by indentation and repeated-character output.

Risks: Callers must call `Flush()` or close/flush the underlying file after writer completion. Partial writes are silent, which can hide disk or pipe failures. Copying is disabled to avoid duplicate buffer ownership assumptions.

Test signals: Verify exact bytes for buffered writes, boundary flushes, `PutN()` across multiple buffer-size chunks, explicit final flush, behavior with very small buffers, and simulated partial `fwrite()` if a test harness can intercept it.
