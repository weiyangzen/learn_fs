# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_base32.py

## Purpose
This file tests Tahoe's base32 utility functions against Python's standard base32 encoding and known examples. It ensures round-trip correctness, byte return types, padding removal, lowercase output, and invalid input detection.

## Important APIs, Types, And Functions
The `Base32` class tests `base32.b2a`, `base32.a2b`, `base32.b2a_or_none`, and `base32.could_be_base32_encoded`. Hypothesis supplies arbitrary byte strings up to 100 bytes.

## Control Flow
The property test encodes random input with Tahoe and Python `base64.b32encode`, strips padding, lowercases the Python result, then decodes Tahoe output and checks equality. Example tests validate a known value, `None` handling, and assertion failure for an invalid string containing disallowed characters.

## State, Persistence, And Dependencies
There is no state or persistence. The test depends on Python's `base64` module as an oracle.

## Risks And Test Signals
This guards a low-level encoding used in caps, storage indexes, server ids, and UI abbreviations. Any change in alphabet, padding behavior, output type, or validation strictness is highly visible.
