# sources/user-network-fs/impacket/tests/misc/test_ip6_address.py

Purpose: Tests IPv6 address parsing, byte conversion, canonical string compression, and malformed input handling.

Important APIs, types, and functions: Uses `IP6_Address`, `as_bytes`, `as_string`, `six.assertRaisesRegex`, and local `hexl`.

Control flow: Iterates valid IPv6 strings, asserts exact 16-byte hex output and canonical compressed string output, then checks several invalid forms raise expected error messages.

State and persistence behavior: Pure in-memory value parsing.

Dependencies and integration points: Supports packet/address code that consumes Impacket's `IP6_Address` helper.

Risks: IPv6 zero-compression and malformed-colon detection are easy to mishandle. Additional invalid cases are noted but commented out, so coverage is not exhaustive.

Test signals: Covers full addresses, internal zero compression, leading/trailing double-colon forms, all-zero address, oversized group rejection, and triple-colon rejection.
