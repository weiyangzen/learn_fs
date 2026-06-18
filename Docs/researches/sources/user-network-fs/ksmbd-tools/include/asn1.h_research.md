<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/asn1.h -->
# sources/user-network-fs/ksmbd-tools/include/asn1.h

## Purpose

Declares a compact ASN.1 DER/BER decoder and encoder surface used by SPNEGO/Kerberos negotiation code.

## Important APIs, Types, and Functions

Defines ASN.1 classes, tags, primitive/constructed flags, error codes, well-known OID arrays for SPNEGO, NTLMSSP, KRB5, KRB5U2U, and MSKRB5, `struct asn1_ctx`, `struct asn1_octstr`, and read/write helpers such as `asn1_open`, `asn1_header_decode`, `asn1_oid_decode`, `asn1_header_encode`, and `asn1_oid_encode`.

## Control Flow

Callers initialize a context over a buffer, decode headers to get class/constructed/tag/end-of-content, read octets or OIDs, and use encoder helpers to construct headers and OID payloads.

## State and Persistence Behavior

State is cursor-based in `asn1_ctx`: begin, end, pointer, and error. The OID arrays are header-level static data in each translation unit that includes the header.

## Dependencies and Integration Points

Integrated with management/spnego and optional Kerberos support; depends only on basic C types.

## Risks and Edge Cases

The header defines non-const static OID arrays, which creates per-translation-unit copies and permits accidental mutation. Length and EOC handling are security-sensitive for untrusted negotiation blobs.

## Test Signals

Tests should cover DER header lengths, invalid lengths, OID round trips for all declared mechanisms, empty/truncated buffers, and nested constructed values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/asn1.h -->
