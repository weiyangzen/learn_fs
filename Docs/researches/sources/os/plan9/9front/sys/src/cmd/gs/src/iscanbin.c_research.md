# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscanbin.c

Implements binary token scanning and writing for Ghostscript Level 2 binary object support. It recognizes token byte values 128 through 159, including binary object sequences, fixed and encoded numbers, booleans, strings, system/user names, and numeric arrays. Numeric decoding uses format metadata from `ibnum.h` and handles endian and float representation variants.

Binary object sequences are parsed into a preallocated ref array, then resized after determining how much payload is object records versus string data. The parser supports null, integer, real, name, evaluated name, boolean, string, array, mark, and a Ghostscript dictionary extension. It can suspend and resume while reading strings or object sequence payloads.

The write side is `encode_binary_token`, which serializes refs into binary sequence records, including array/dictionary offsets and string/name character offsets. The file depends on name tables, dictionaries, object stack support, VM-space checks, and scanner continuation state.
