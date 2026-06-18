<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.c -->
# sources/user-network-fs/cifs-utils/asn1.c

## Purpose

`asn1.c` implements a small BER/ASN.1 writer used by cifs-utils for CLDAP query generation and SPNEGO-related encoding. It allocates expandable talloc-backed buffers, writes primitive bytes and octet strings, encodes OID strings, and fixes up nested tag lengths after payloads are written.

## Important APIs, Types, and Functions

The public functions are `asn1_init`, `asn1_free`, `asn1_write`, `asn1_write_uint8`, `asn1_push_tag`, `asn1_pop_tag`, `ber_write_OID_String`, `asn1_write_OID`, and `asn1_write_OctetString`. `asn1_push_tag` records the current offset in a `struct nesting`; `asn1_pop_tag` computes payload length and rewrites BER short or long-form length bytes.

## Control Flow

Callers create `ASN1_DATA`, push a tag, write nested fields, and pop the tag once the payload is complete. `asn1_write` grows `data->data` with `talloc_realloc` and advances `ofs`. `asn1_pop_tag` initially assumes a one-byte length placeholder; if the payload exceeds 127, 255, 65535, or 16777215 bytes, it appends padding bytes, `memmove`s payload data forward, and emits the corresponding long-form BER length.

## State and Persistence Behavior

All state is in `struct asn1_data`: the byte buffer, allocated length, current offset, nested tag stack, and sticky `has_error` flag. Once an error is set, later writes fail. No process-global or filesystem state is used. Returned OID blobs and ASN.1 buffers are talloc-owned and must be freed with `data_blob_free` or `asn1_free`.

## Dependencies and Integration Points

The file depends on `talloc`, `stdint`, `stdbool`, `data_blob.h`, and `asn1.h`. `cldap_ping.c` uses the tag writer to build LDAP search requests. SPNEGO helpers can also rely on OID encoding semantics shared with Samba-derived code.

## Risks and Edge Cases

Length parameters mix signed `int` with `size_t`, so negative lengths from a bad caller would be dangerous. `ber_write_OID_String` assumes the BER representation is no longer than the input string and only supports component values up to the emitted 35-bit pattern implied by the shifts. `asn1_write_OctetString` does not individually check each nested write and relies on the sticky error flag. Large nesting payloads use in-place `memmove`, so offset correctness is critical.

## Test Signals

Tests should compare encoded tags, OIDs, and octet strings against known BER vectors for short and long lengths, inject allocation failures if possible, and exercise CLDAP query generation as an integration signal. Boundary lengths of 127, 128, 255, 256, 65535, and 65536 are important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/asn1.c -->
