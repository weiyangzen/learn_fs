<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c -->
# sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c

## Purpose
This file provides fallback BSD-style Base64 encoding and decoding when the platform lacks `b64_ntop` and `__b64_ntop`. It also adds URL/file-name-safe Base64 encoding.

## Important APIs, Types, and Functions
Compiled only when neither `HAVE_B64_NTOP` nor `HAVE___B64_NTOP` is defined, the exported functions are `b64_enc`, `b64_ntop`, `base64url_encode`, and `b64_pton`. `Base64`, `Base64url`, and `Pad64` define the encoding alphabets and padding. `b64_enc` is the shared encoder; `b64_ntop` uses the normal alphabet, while `base64url_encode` uses `-` and `_`.

## Control Flow
`b64_enc` processes complete 3-byte groups into four 6-bit indexes, handles a final 1- or 2-byte group with `=` padding, checks target capacity, and NUL-terminates the output. `b64_pton` skips whitespace, decodes Base64 characters through a four-state machine, stops at padding, validates padding position and trailing whitespace, verifies unused low bits are zero, and returns decoded byte count or `-1`.

## State and Persistence Behavior
The functions are stateless and operate only on caller-provided buffers. They do not allocate or persist data.

## Dependencies and Integration Points
The code depends on `config.h`, C library headers, and `bsd-base64.h`. It supplies compatibility for support code needing Base64 across platforms without libc/resolver Base64 helpers.

## Risks and Test Signals
Risks include caller-provided buffer sizing, `int` return truncation for very large encoded lengths, and `isspace(ch)` receiving values from signed `char` inputs outside ASCII. `b64_pton` can be used in length-counting mode with `target == NULL`, which callers must understand. Test signals include RFC 4648 known vectors, URL-safe output checks, whitespace-tolerant decode, bad padding rejection, target-too-small rejection, and builds on platforms with and without native Base64 APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/bsd-base64.c -->
