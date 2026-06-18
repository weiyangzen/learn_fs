# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/uuid_stream.c

## Purpose
Provides endian-specific UUID encode/decode helpers for 16-byte octet streams.

## Main Entry Points
- `uuid_enc_le()` and `uuid_dec_le()` encode/decode UUID time fields as little-endian, followed by raw clock sequence and node bytes.
- `uuid_enc_be()` and `uuid_dec_be()` do the same with big-endian time fields.

## Dependencies
Depends on machine endian helpers `le32enc`, `le16enc`, `le32dec`, `le16dec`, `be32enc`, `be16enc`, `be32dec`, and `be16dec`.

## Risks And Notes
These helpers are documented as convenience functions outside the core DCE RPC API. Callers must provide at least 16 bytes of buffer storage and valid UUID pointers.
