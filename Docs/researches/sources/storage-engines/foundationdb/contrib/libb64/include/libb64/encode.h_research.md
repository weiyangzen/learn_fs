# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/encode.h

## Purpose
`encode.h` provides a C++ stream/string wrapper around the C libb64 encoder.

## Important APIs, Types, And Functions
It defines `BUFFERSIZE 8192`. Inside namespace `base64`, `struct encoder` owns a `base64_encodestate` and buffer size. Methods include `encode(char)`, `encode(const char*, int, char*)`, `encode_end(char*)`, `encode(std::istream&, std::ostream&)`, and static `from_string(std::string)`.

## Control Flow
Stream encoding initializes C encode state, allocates plaintext and expanded code buffers, reads chunks from the input stream, writes encoded chunks to the output stream, then calls `encode_end` to flush padding and final newline. State is reset and buffers are freed before return.

## State And Persistence Behavior
Encoder state is per object and reset around stream calls. Heap buffers are local to stream encoding. No external persistence occurs.

## Dependencies And Integration Points
It includes `<iostream>`, `<sstream>`, and `cencode.h` under `extern "C"`. C++ consumers get a header-only convenience layer over the C object files in `libb64`.

## Risks And Edge Cases
Manual buffer management is not exception-safe. Output includes line wrapping and a trailing newline from the C encoder. Direct low-level `encode` calls require explicit state initialization and finalization by the caller.

## Test Signals
Tests should cover string and stream encoding, padding tails, empty input, line wrapping, binary input, and round trips through `decode.h`.
