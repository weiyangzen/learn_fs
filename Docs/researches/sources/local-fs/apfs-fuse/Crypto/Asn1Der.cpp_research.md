# File Research: sources/local-fs/apfs-fuse/Crypto/Asn1Der.cpp

## Role

`Asn1Der.cpp` implements a small ASN.1 DER decoder and debug dumper used by APFS key-management parsing.

## Core Behavior

- `der_decode_tag()` parses short-form and high-tag-number DER tags, preserving class/constructed bits in a packed `uint64_t`.
- `der_decode_len()` parses short and long-form definite lengths.
- `der_decode_tl()` validates an expected tag, returns the body pointer, and checks body bounds.
- `der_decode_constructed_tl()` and `der_decode_sequence_tl()` return constructed body ranges.
- `der_decode_uint()` reads a fixed-width big-endian unsigned integer into `uint64_t`.
- `der_decode_uint64()` decodes a tagged integer-like value up to 8 bytes.
- `der_decode_octet_string_copy()` validates exact length and copies the payload.
- `der_dump()` recursively prints parsed TLV records and hex payloads for debugging.

## Important Dependencies

- Implements declarations from `Crypto/Asn1Der.h`.
- Used by `ApfsLib/KeyMgmt.cpp` for APFS wrapped-key and HMAC metadata parsing.

## Notable Limitations And Risk Areas

- Length parsing uses pointer arithmetic such as `der + nb` and `der + len`; malformed huge lengths can be risky in general C++ pointer arithmetic even though bounds checks follow.
- DER canonical constraints are not fully enforced: minimal length encoding, indefinite-length rejection semantics, integer sign/canonical form, and high-tag minimal form are not deeply validated.
- `der_decode_len()` rejects `(der + nb) >= der_end`, which also rejects a long-form length field ending exactly at `der_end`; that is conservative but slightly stricter than pure byte availability.
- `der_dump()` prints to stdout and should remain debug-only.
