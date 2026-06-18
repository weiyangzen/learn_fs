# sources/user-network-fs/impacket/tests/dot11/test_wps.py

Purpose: Tests WPS TLV container serialization/deserialization with typed value builders.

Important APIs, types, and functions: Uses `wps.TLVContainer`, `wps.StringBuilder`, `wps.ByteBuilder`, `wps.NumBuilder`, `append`, `to_ary`, `from_ary`, and `first`.

Control flow: Builds a TLV container with builders for string, byte, and two-byte numeric types, appends known and unknown TLV kinds, serializes to an array, reparses into a second container, and compares values plus serialized output.

State and persistence behavior: TLV state is held in memory as array-like bytes. No persistence.

Dependencies and integration points: Supports WPS information element parsing used by wireless management-frame vendor-specific payloads.

Risks: Unknown TLV kinds must round-trip as raw byte arrays. Builder mismatches could alter byte order or value type on reparse.

Test signals: Validates normal builder dispatch, unknown-kind preservation, `first` lookup semantics, and stable serialization round-trip.
