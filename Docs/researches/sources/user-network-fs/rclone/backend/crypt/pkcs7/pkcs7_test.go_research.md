# sources/user-network-fs/rclone/backend/crypt/pkcs7/pkcs7_test.go

Purpose: Verifies PKCS#7 padding behavior for successful round trips, malformed padding, and invalid block size panics.

Important APIs, types, and functions: `TestPad` enumerates expected padded byte strings for block sizes 8 and 16 and immediately unpads them. `TestUnpad` enumerates error cases for empty, unaligned, too-long, zero-length, and inconsistent padding.

Control flow: Table-driven assertions compare exact padded strings, then assert `Unpad` recovers the original bytes. Error tests assert both the exact exported error value and a nil result. Panic assertions cover `n == 1` and `n == 256` for both functions.

State and persistence behavior: The tests use in-memory byte slices only and have no external state.

Dependencies and integration points: Uses `testing`, `fmt`, and testify assertions. It gives low-level confidence to any crypt code consuming `pkcs7.Pad` and `pkcs7.Unpad`.

Risks: Tests focus on fixed examples rather than randomized block sizes or all possible malformed suffixes. They intentionally assert exact error values, so changing error taxonomy is a compatibility-visible change.

Test signals: Passing tests indicate padding bytes, full-block padding, round-trip slicing, error classification, and panic boundaries match expectations.
