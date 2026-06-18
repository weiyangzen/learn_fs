# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_base62.py

## Purpose
This file tests Tahoe's base62 encoding/decoding, including ordinary byte round trips, known stable encodings, size calculations, and bit-length-limited encode/decode operations.

## Important APIs, Types, And Functions
`Base62` uses helpers `byteschr`, `insecurerandstr`, `_test_num_octets_that_encode_to_this_many_chars`, and `_test_roundtrip`. It tests `base62.b2a`, `base62.a2b`, `base62.b2a_l`, `base62.a2b_l`, `base62.chars`, `num_chars_that_this_many_octets_encode_to`, and `num_octets_that_encode_to_this_many_chars`.

## Control Flow
The Hypothesis roundtrip covers arbitrary byte strings. Known-value tests pin algorithm output. Edge-case tests cover zero and small byte patterns. `test_odd_sizes` randomly chooses bit lengths, masks unused low-order bits, encodes exactly that bit length, decodes it, and verifies result size and equality.

## State, Persistence, And Dependencies
There is no persistence. Randomized tests use Python's `random` without a fixed seed for some cases, so failures may be less reproducible than Hypothesis failures.

## Risks And Test Signals
The stable known-value tests warn against algorithm changes that would break compatibility. The `test_num_octets_that_encode_to_this_many_chars` method has early `return` statements after the first assertion, leaving later intended checks unreachable; that is a test-coverage risk.
