# sources/storage-engines/foundationdb/contrib/libb64/include/libb64/decode.h

## Purpose
`decode.h` provides a C++ stream/string wrapper around the C libb64 decoder.

## Important APIs, Types, And Functions
Inside namespace `base64`, `struct decoder` owns a `base64_decodestate` and buffer size. Methods include `decode(char)`, `decode(const char*, int, char*)`, `decode(std::istream&, std::ostream&)`, and static `from_string(std::string)`.

## Control Flow
Stream decoding initializes C decode state, allocates code and plaintext buffers, reads chunks from the input stream, decodes each chunk, writes decoded bytes to the output stream, resets state, and frees buffers. `from_string` wraps stringstreams around this stream API.

## State And Persistence Behavior
Decoder state is per object and reset around stream calls. Heap buffers are allocated per stream decode call and freed before return. No persistent storage is touched.

## Dependencies And Integration Points
It includes `<iostream>` and `libb64/encode.h`; the latter supplies `BUFFERSIZE` and includes `<sstream>`, which `from_string` relies on. It includes `cdecode.h` in an `extern "C"` block. C++ users can include this header without linking a separate wrapper source, but still need the C decoder object code.

## Risks And Edge Cases
Including `encode.h` only to obtain `BUFFERSIZE` couples decode to encode. Manual `new[]`/`delete[]` lacks RAII if stream operations throw exceptions. Strict base64 validation is inherited from the permissive C decoder. The decoder state is uninitialized until stream decode or caller-managed direct decode initializes it.

## Test Signals
Tests should cover `from_string`, stream decoding with chunked inputs, binary output, empty input, invalid characters, and exception-safety expectations if streams are configured to throw.
