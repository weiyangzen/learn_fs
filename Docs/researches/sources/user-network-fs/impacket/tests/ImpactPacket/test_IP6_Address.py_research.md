# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Address.py

## Purpose

`test_IP6_Address.py` validates IPv6 address parsing, conversion, compression, unicode input, and scope-id handling.

## Important APIs, Types, And Functions

It imports `unittest` and `IP6_Address`. `TestIP6_Address` defines `test_construction()`, `test_unicode_representation()`, `test_conversions()`, `test_compressions()`, and `test_scoped_addresses()`.

## Control Flow

The tests construct addresses from full text, byte lists, unicode strings, compressed forms, and scoped forms. They assert success for valid forms, exceptions for oversized/undersized/malformed/empty forms, byte/text round trips, compressed versus full formatting, and scope-id/unscoped-address accessors.

## State And Persistence Behavior

State is local address literals and expected byte lists. There is no persistence.

## Dependencies And Integration Points

The file exercises `IP6_Address.IP6_Address`, `as_string()`, `as_bytes()`, `get_scope_id()`, and `get_unscoped_address()`.

## Risks And Edge Cases

The tests do not inspect exception types/messages and do not cover IPv4-mapped addresses, multiple `::` errors, lowercase normalization, or every hextet boundary.

## Test Signals

Passing tests signal stable validation, compression, round-trip conversion, and scope handling for representative IPv6 addresses.
