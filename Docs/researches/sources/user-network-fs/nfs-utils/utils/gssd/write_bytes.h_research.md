# sources/user-network-fs/nfs-utils/utils/gssd/write_bytes.h

Purpose: provides inline serialization/deserialization helpers for bounded byte buffers and simple XDR-like 32-bit-aligned GSS buffers.

Important APIs: `write_bytes()`, `WRITE_BYTES`, `write_buffer()`, and `write_oid()` append native-endian length-prefixed values to a caller-managed buffer. `get_bytes()` and `get_buffer()` parse native-endian fields and allocate GSS buffers. `xdr_get_u32()`, `xdr_get_buffer()`, `xdr_write_u32()`, and `xdr_write_buffer()` handle network-byte-order 32-bit fields and padded XDR buffers.

Control flow: every helper advances the caller's pointer only after bounds checks pass. Reads and writes validate `end` boundaries and pointer wraparound. Buffer getters allocate exact payload length and copy payload into newly owned memory.

State and persistence: no global state; persistence is in caller-provided serialized buffers and allocated result buffers that callers must release.

Dependencies and integration: used by GSS context/channel serialization code; depends on GSSAPI buffer/OID layouts, `malloc`, `memcpy`, and byte-order conversion.

Risks: native-endian helpers are not portable wire formats; zero-length buffers currently attempt `malloc(0)` and can be treated as failure depending on libc behavior. `xdr_write_buffer()` writes padded bytes from `arg->value`, so callers must ensure padding bytes are readable. Test signals include boundary overflow checks, malformed lengths, zero-length buffers, XDR padding behavior, and pointer advancement after failure.
