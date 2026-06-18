# sources/user-network-fs/impacket/impacket/uuid.py

## Purpose

`uuid.py` provides Impacket's UUID/GUID conversion helpers. It generates simple 16-byte identifiers and converts between binary DCE/RPC GUID layout, canonical string layout, UUID/version tuples, and packed UUID-plus-version values used by RPC interface bindings.

## Important APIs, Types, And Functions

`EMPTY_UUID` is the all-zero 16-byte value. `generate()` returns 16 random bytes assembled from four 31-bit random integers. `bin_to_string()` formats mixed-endian RPC GUID bytes. `string_to_bin()` accepts canonical dashed UUIDs or 32-character hex strings. `stringver_to_bin()` packs `major.minor` as little-endian shorts. `uuidtup_to_bin()`, `bin_to_uuidtup()`, `string_to_uuidtup()`, and `uuidtup_to_string()` bridge Impacket tuple forms.

## Control Flow

Conversions use regular expressions plus `struct.pack`/`unpack`. Dashed strings are parsed as Microsoft variant 2/DCE wire layout: first three fields little-endian, remaining fields big-endian. `string_to_uuidtup()` appends `" 1.0"` before searching so missing versions default to `1.0`.

## State And Persistence Behavior

The module has no mutable state or persistence. Random output comes from Python `random.randrange`, not a durable namespace or cryptographic generator.

## Dependencies And Integration Points

It depends on `re`, `binascii`, `random.randrange`, and `struct`. It is used across DCERPC binding modules, endpoint mapper code, packet parsers, and tests needing RPC interface UUID bytes.

## Risks And Edge Cases

`generate()` is not RFC-compliant or cryptographically strong. `string_to_bin()` assumes a dashed UUID regex match and will fail for malformed input; undashed input is blindly unhexlified. `uuidtup_to_bin()` silently returns `None` for non-two-element tuples. `bin_to_uuidtup()` uses `assert` for length checking. `uuidtup_to_string()` expects numeric version tuple form, while `string_to_uuidtup()` returns the version as a string.

## Test Signals

Tests should round-trip canonical UUIDs through binary and tuple forms, validate mixed-endian ordering against known RPC UUIDs, cover default `1.0` extraction, malformed strings, invalid tuple length, and string-version versus numeric-version tuple expectations.
