# sources/user-network-fs/libsmb2/lib/asn1-ber.c

Purpose: Implements BER/ASN.1 parsing and encoding primitives for simple scalar, OID, byte, and string values.

Important APIs/functions: Byte cursors are handled by `asn1ber_next_byte` and `asn1ber_out_byte`. Parse helpers include `asn1ber_length_from_ber`, `ber_typecode_from_ber`, `ber_typelen_from_ber`, integer decoders, OID decoder, and byte/string decoders. Encode helpers include `asn1ber_ber_from_length`, `asn1ber_ber_from_typelen`, integer encoders, OID encoder, byte/string encoders, length reservation, and `asn1ber_annotate_length`.

Control flow: Decoders consume from `actx->src` using `src_tail` and update output values after type/length validation. Encoders append to `actx->dst` via `dst_head`, optionally reserve length bytes, emit content, then back-annotate actual length with `memmove` if fewer length bytes were needed.

State/persistence: State is held in `struct asn1ber_context`: source cursor, destination cursor, buffer sizes, and `last_error`. No global state. Cursor advances are permanent on partial parse failures.

Dependencies/integration: Depends on errno constants and `asn1-ber.h` tags/context definitions. It is a standalone helper for BER consumers in libsmb2; callers must initialize context fields.

Risks: Bounds checks are present at byte I/O boundaries, but APIs trust non-NULL output pointers in several paths. `asn1ber_ber_from_uint64` initializes `bytesneeded` to 4 while examining 64-bit values, which can under-encode large unsigned 64-bit values. Integer length decoders handle only short one-byte length forms for int values, while generic length decoding supports long form. OID length validation compares BER byte length to element capacity, which is conservative but not an exact element-count limit.

Test signals: Fuzz BER decoders with malformed length/type/value combinations, test cursor positions after failure, test long-form lengths, signed integer sign extension, OID base-128 continuation, back-annotated lengths, and 64-bit unsigned values above 32 bits.
