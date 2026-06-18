# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iscanbin.c

Purpose: implements Ghostscript Level 2 binary token scanning and binary object sequence writing support.

Scanner responsibilities:
- Recognizes binary token byte values 128-159 for numbers, booleans, short strings, system/user names, numeric arrays, and binary object sequences.
- Decodes fixed, integer, and floating formats with explicit endian/native/IEEE variants.
- Supports refill-safe continuation for binary strings, numeric arrays, and binary object sequences.
- Parses binary object sequences into preallocated ref arrays, then reads trailing string/name data and fixes up names, evaluated names, arrays, and Ghostscript's dictionary extension.

Binary object sequence handling:
- Preallocates worst-case object refs from the declared byte length.
- Allocates/reallocates one trailing string area once the smallest string offset is known.
- Supports strings, names from raw bytes or system/user name tables, executable/evaluated names, arrays, marks, nulls, numbers, booleans, and dictionary objects.
- Dictionary support is an extension: even sizes encode key/value pairs; size 1 encodes an indirect dictionary reference.

Writing support:
- `encode_binary_token` serializes refs into 8-byte binary sequence object records for nulls, marks, integers, reals, booleans, arrays, dictionaries, strings, and names.
- It tracks separate ref and character offsets and adapts real encoding to the configured binary object format.

Dependencies: `btoken.h`, binary-number decoding from `ibnum.h`, dictionary/name lookup, VM-space store checks, dynamic scanner state from `iscan.h`, and stream buffer APIs.
