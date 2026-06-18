# sources/distributed-fs/tahoe-lafs/src/allmydata/util/base32.py

## Purpose

This module implements Tahoe-LAFS base32 encoding and validation using the lowercase RFC3548 alphabet. It supplies regex fragments and trailing-character checks used by capability parsers, storage index displays, and other binary-to-text identifiers.

## APIs and control flow

`b2a()` base32-encodes bytes, strips padding, and lowercases. `a2b()` validates with `could_be_base32_encoded()`, restores padding, uppercases, and decodes via Python `base64`. `b2a_or_none()` preserves `None`. The trailing-character helpers build regex fragments such as `BASE32CHAR_3bits`, `BASE32CHAR_1bits`, and `BASE32STR_anybytes` so callers can validate exact byte lengths without accepting impossible low bits.

## State, dependencies, risks, and tests

Module state consists of translation tables, constants mapping encoded lengths to original byte lengths, and `s8`, a precomputed table for cheap final-character validity. Dependencies are `base64`, typing, and `precondition`.

This is compatibility-sensitive because URI regexes in `uri.py` depend on the exact alphabet and trailing-bit restrictions. Risks include accepting uppercase only after validation, rejecting non-canonical encodings, and assertion/precondition behavior being disabled or changed. Test signals should cover round-trips for all short byte lengths, invalid trailing characters, empty bytes, `None`, URI regex integration, and compatibility with historical Tahoe caps.
