# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucUri.cc

Purpose: implements URL percent-encoding and decoding for ASCII/binary byte strings, adapted from URI-Encode-C with XRootD naming and table changes.

Important APIs, types, and functions: static `hexval` maps ASCII hex digits to nibbles. `uri_encode_tbl` maps each byte to either a two-character hex code or zero bytes to indicate no encoding. `Decode()` decodes `%XX` sequences when both hex digits are valid. `Encode()` has allocating and caller-buffer variants. `Encoded()` computes the required output size including the null byte.

Control flow: `Decode()` scans input, copies normal bytes, and converts valid percent sequences while leaving invalid sequences mostly unchanged by copying the `%` then continuing. `Encode(char*)` scans each byte, emits `%HH` for entries present in the encode table, otherwise copies the byte. Allocating `Encode(char**)` computes size with `Encoded()`, mallocs, and delegates.

State and persistence: state is read-only static lookup tables. Allocating `Encode()` returns heap memory that callers must free. No locking or persistence is needed.

Dependencies and integration points: depends on C allocation/string headers and `XrdOucUri.hh`. It integrates with CGI/query construction and protocol code needing URL-safe strings.

Risks and test signals: `Encoded()` indexes `uri_encode_tbl[((unsigned int)src[i]) << 1]` without casting `src[i]` to unsigned char, so negative signed chars can index before the table. Allocating `Encode()` returns `0` both for allocation failure and potentially empty encoded length ambiguity through the length return. Tests should cover all unreserved/reserved byte classes, invalid percent sequences, high-bit bytes on signed-char platforms, allocation API ownership, and exact size from `Encoded()`.
