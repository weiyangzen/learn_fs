# sources/user-network-fs/ksmbd-tools/tools/asn1.c

## Purpose

`asn1.c` implements small ASN.1/BER decoding and encoding helpers used by ksmbd SPNEGO/Kerberos negotiation. It parses headers, object identifiers, octet payloads, and raw buffers, and it builds simple definite-length headers/OID encodings for response tokens. The source was read as a complete 391-line file.

## Important APIs, Types, and Functions

Public functions are `asn1_open`, `asn1_header_decode`, `asn1_octets_decode`, `asn1_read`, `asn1_oid_decode`, `asn1_header_len`, `asn1_oid_encode`, and `asn1_header_encode`. Internal helpers decode octets, high-tag-number tags, identifier octets, lengths, EOC markers, and OID subidentifiers. State is held in `struct asn1_ctx` from `asn1.h`.

## Control Flow

Callers initialize a context with `asn1_open`, then repeatedly decode headers and consume payloads until the returned EOC pointer is reached. OID decode reads the compressed first two subidentifiers and then variable-length base-128 subids. Encoding first computes nested header sizes, then writes identifier octets and short or long-form lengths before payload bytes are copied by the caller.

## State and Persistence Behavior

All parser state is cursor state inside `asn1_ctx`: `begin`, `end`, `pointer`, and `error`. The module allocates output buffers with GLib allocators and leaves ownership to callers. There is no file or process-global persistence.

## Dependencies and Integration Points

It depends on GLib allocation and is integrated by `management/spnego.c` for SPNEGO OID/token parsing and response construction.

## Risks and Edge Cases

Length decoding rejects lengths beyond the remaining buffer, which is essential for untrusted network tokens. However, some integer math mixes pointer differences and unsigned sizes; very large inputs should be fuzzed. `asn1_octets_decode` assumes a definite EOC pointer. Encoding supports up to four length octets and simple single-octet tags, matching current SPNEGO needs rather than a full ASN.1 implementation.

## Test Signals

ASN.1 fuzzing with truncated, indefinite, overlong, and malformed OIDs is the main signal. SPNEGO token interoperability tests and round-trip OID/header encode/decode tests should cover the expected Kerberos OIDs.
