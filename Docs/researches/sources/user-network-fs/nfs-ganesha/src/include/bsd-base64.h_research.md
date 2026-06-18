<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h -->
# sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h

## Purpose
`bsd-base64.h` declares BSD/ISC-style base64 encode/decode helpers and a base64url encoder used by Ganesha support code.

## Important APIs, types, and functions
- `b64_ntop()` encodes binary source bytes into base64 text.
- `b64_pton()` decodes base64 text into binary bytes.
- `base64url_encode()` encodes source bytes using URL-safe base64.
- Compatibility macros `__b64_ntop` and `__b64_pton` alias the public names.

## Control flow
Callers provide source pointer/length, target buffer, and target size. Implementations return encoded/decoded lengths or an error code according to the BSD routines' convention.

## State and persistence
The header has no state. Encoded output is written to caller-owned buffers.

## Dependencies and integration points
It depends on `<sys/types.h>` for `u_char`. It integrates with code that needs textual representation of binary tokens, handles, keys, or protocol fields.

## Risks
- Callers must size target buffers correctly and check return values.
- Standard base64 and base64url alphabets are not interchangeable; callers must choose the correct function for protocol context.
- SPDX is marked unknown 0BSD while comments include ISC/IBM permission text; license metadata may require review.
- The include guard closing comment names `_BSD_BINRESVPORT_H`, which is harmless but misleading.

## Test signals
- Known-vector tests should cover empty input, one/two/three-byte groups, padding, invalid characters, target-too-small behavior, and URL-safe output.
- Fuzz tests should decode arbitrary input without overruns.
- License scanning should verify accepted metadata for vendored code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h -->
