# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.h

This header defines the bit-reader interface for the MP3 decoder. `struct mad_bitptr` contains `byte`, `cache`, and `left`, representing the current byte address, cached byte contents, and number of unread bits left in that byte.

It declares initialization, length calculation between two bit pointers, next-byte discovery, skip/read/write operations, and CRC calculation. `mad_bit_finish` is a no-op macro because the bit pointer owns no dynamic memory. `mad_bit_bitsleft` exposes the `left` field directly for performance-sensitive code, especially Layer III Huffman decoding.

The header is included throughout the decode stack: stream synchronization initializes bit pointers; frame header parsing reads bit fields; Layer I/II sample parsing and Layer III side-info/Huffman parsing use it heavily. `mad_bit_write` is declared but not compiled in `bit.c`, so external users should not rely on it unless they also enable/provide that implementation.
