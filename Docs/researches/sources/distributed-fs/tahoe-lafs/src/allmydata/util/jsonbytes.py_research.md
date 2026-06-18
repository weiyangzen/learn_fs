# sources/distributed-fs/tahoe-lafs/src/allmydata/util/jsonbytes.py

## Purpose

This module makes JSON encoding tolerate bytes in values and keys. It is used by logging and diagnostics where Tahoe often has byte-oriented protocol data but JSON serializers require text.

## APIs and control flow

`bytes_to_unicode(any_bytes, obj)` recursively converts bytes to Unicode. With `any_bytes=False`, bytes must be valid UTF-8; with `True`, decoding uses `backslashreplace` for arbitrary bytes. Dict keys and values are converted, and lists/sets/tuples become lists. `UTF8BytesJSONEncoder` and `AnyBytesJSONEncoder` apply that conversion in `default`, `encode`, and `iterencode`. `dumps()` selects the encoder with an `any_bytes` keyword; `dumps_bytes()` UTF-8 encodes the JSON string. `loads` and `load` are stdlib aliases.

## State, dependencies, risks, and tests

There is no state. Dependency is stdlib `json`. Integration includes Foolscap logging wrappers and Eliot file destinations.

Risks include sets/tuples losing type identity as JSON arrays, key collisions after byte-to-text conversion, strict UTF-8 mode raising late during logging, and `__all__` omitting `dumps_bytes` even though it is useful. Test signals should cover bytes keys/values, nested structures, arbitrary bytes, strict failures, sets/tuples, JSON loads compatibility, and logging serialization paths.
