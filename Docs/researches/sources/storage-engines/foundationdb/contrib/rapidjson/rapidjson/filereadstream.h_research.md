# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filereadstream.h

Purpose: `FileReadStream` adapts a `std::FILE*` plus caller-owned buffer to RapidJSON's input stream concept for byte-oriented parsing.

Important APIs and types: The class exposes `typedef char Ch`, constructor `FileReadStream(std::FILE*, char*, size_t)`, `Peek()`, `Take()`, `Tell()`, and `Peek4()` for encoding detection. Output-stream functions are present only to satisfy concept shape and assert if called.

Control flow: Construction asserts a non-null file and a buffer of at least four bytes, then performs an initial `Read()`. `Take()` returns the current byte and advances through `Read()`. `Read()` increments inside the current buffer until exhausted, then uses `fread()` to refill. A short read appends a `'\0'` sentinel, advances `bufferLast_`, and marks EOF.

State and persistence behavior: Runtime state tracks `fp_`, `buffer_`, `bufferSize_`, `bufferLast_`, `current_`, `readCount_`, cumulative `count_`, and `eof_`. It reads from the file but does not own or close it. `Tell()` is derived from fully consumed chunks plus current buffer offset.

Dependencies and integration points: It includes `stream.h` and `<cstdio>`. Reader/document parsing can use it directly, and encoded input streams use `Peek4()` to detect BOM/UTF type.

Risks: The caller must keep the file and buffer alive. `fread()` errors are not distinguished from EOF. `Peek()` after EOF returns the sentinel. Buffer sizes below four violate assumptions needed by encoding detection.

Test signals: Parse from small and large buffers, verify `Tell()` across buffer refills, confirm EOF sentinel behavior, check `Peek4()` availability near buffer boundaries, and exercise short-read and empty-file parsing.
