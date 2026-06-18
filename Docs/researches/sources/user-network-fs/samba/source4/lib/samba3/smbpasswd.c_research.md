# sources/user-network-fs/samba/source4/lib/samba3/smbpasswd.c

## Purpose

`smbpasswd.c` implements helpers for converting smbpasswd hash fields between textual 32-character hex and Samba's `struct samr_Password` binary hash representation.

## Important APIs, Types, and Functions

`smbpasswd_gethexpwd()` parses a hash string into a talloc-allocated `struct samr_Password`. `smbpasswd_sethexpwd()` formats a password hash as 32 hex characters or returns smbpasswd placeholder strings for NULL hashes based on account-control flags.

## Control Flow

Parsing rejects NULL input, allocates a password object, and calls `strhex_to_str()` to decode exactly 16 bytes from 32 hex characters. If decoding does not produce 16 bytes, it frees and returns NULL. Formatting calls `hex_encode_talloc()` when a password is present; otherwise it emits `NO PASSWORDXXXXXXXXXXXXXXXXXXXXX` when `ACB_PWNOTREQ` is set, or 32 `X` characters when no hash is stored.

## State and Persistence Behavior

The helpers do not read or write smbpasswd files directly. They allocate converted values under the caller's talloc context. The binary hash data is sensitive credential material and persists in memory until the caller frees it.

## Dependencies and Integration Points

It depends on Samba utility conversion helpers, generated SAMR account-control flags, and `samba3.h`. The private `smbpasswdparser` library exposes these helpers to Samba3 migration/import code.

## Risks and Edge Cases

There is no explicit memory scrubbing before freeing invalid or formatted hashes. Placeholder strings are legacy smbpasswd conventions and must remain exact. The parser accepts whatever `strhex_to_str()` accepts for hex case/format and rejects by decoded length only.

## Test Signals

Tests should cover valid uppercase/lowercase hex, short/long/invalid hex strings, NULL input, formatting NULL with and without `ACB_PWNOTREQ`, and round-tripping a known hash.

Source-read signal: reviewed complete local file (100 lines).
