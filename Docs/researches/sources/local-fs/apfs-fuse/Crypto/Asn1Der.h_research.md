# File Research: sources/local-fs/apfs-fuse/Crypto/Asn1Der.h

## Role

`Asn1Der.h` declares the small DER parsing interface and tag constants used by APFS crypto/key-management code.

## Public Interface

- Defines `der_tag_t` as `uint64_t`.
- Defines high-bit tag flags for constructed and context-specific encodings.
- Enumerates universal ASN.1 tag numbers for common primitive and string types.
- Declares helpers for tag, length, tag-length, constructed body, sequence body, integer, uint64, octet-string-copy decoding, plus `der_dump()`.

## Encoding Model

The code packs ASN.1 class and constructed bits into high bits of `der_tag_t`, with low bits carrying the tag number. This lets call sites compare expected context-specific tags as constants such as `0x8000000000000001U`.

## Notable Limitations And Risk Areas

- The API is pointer-range based and returns `nullptr` on parse failure, so callers must check every step.
- It exposes low-level DER mechanics rather than a structured ASN.1 object model.
