# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.h

`md5.h` declares the standalone MD5 API. It defines `md5_byte_t` as `unsigned char`, `md5_word_t` as `unsigned int`, and `md5_state_t` with two bit-count words, four digest state words, and a 64-byte block buffer.

The exported API is `md5_init`, `md5_append`, and `md5_finish`, wrapped in `extern "C"` for C++ callers. The header documents compile-time or runtime byte-order handling through `ARCH_IS_BIG_ENDIAN`.

It has no Ghostscript-specific types. Consumers can use it as a small standalone hashing interface, subject to MD5's modern cryptographic limitations.
