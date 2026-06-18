# sources/distributed-fs/tahoe-lafs/src/allmydata/util/base62.py

## Purpose

This module implements Tahoe-LAFS base62 conversion over digits, uppercase letters, and lowercase letters. It supports both byte-aligned round-trips and explicit bit-length encodings for compact non-byte-aligned values.

## APIs and control flow

`b2a()` encodes bytes using `b2a_l()` with `len(os) * 8` and asserts the output length maps back to the input byte length. `b2a_l()` treats input bytes as a big-endian integer, repeatedly divides by 62, and emits translated characters sized for the requested bit length. `a2b()` chooses a byte length from encoded-character count, while `a2b_l()` decodes with the explicit bit length. Length helpers use `log_floor` and `log_ceil`.

## State, dependencies, risks, and tests

State is alphabet and translation tables. Dependencies are `mathutil.log_ceil` and `log_floor`. There is no persistence, but serialized values produced elsewhere depend on the exact alphabet and bit-length agreement.

The docstrings warn that `b2a_l()` and `a2b()` are not safely interchangeable when the data length is not byte-aligned. Risks include silent truncation of least-significant bits in explicit-length mode and no strong validation of illegal input bytes before translation. Test signals should cover byte-aligned round-trips, explicit bit lengths, output length formulas, invalid characters, and compatibility with any caller that persists base62 text.
