# sources/distributed-fs/tahoe-lafs/src/allmydata/util/netstring.py

## Purpose

This module implements byte netstring encoding and splitting. Tahoe uses netstrings for unambiguous framing in hashes and URI extensions, where length prefixes prevent concatenation ambiguity.

## APIs and control flow

`netstring(s)` asserts `s` is bytes and returns `<len>:<s>,`. `split_netstring(data, numstrings, position=0, required_trailer=None)` walks from `position`, parses decimal length prefixes up to `numstrings`, validates commas and lengths, and returns `(elements, new_position)`. If `required_trailer` is supplied, all remaining data must match it and is consumed.

## State, dependencies, risks, and tests

There is no state or external dependency. Integration is important: `hashutil` uses `netstring()` for domain-separated tags and input pairs, and `uri.py` packs URI extensions with netstrings.

Risks include assertion-based validation for malformed data, `data.index(b":")` raising raw `ValueError`, potential acceptance of leading-zero length strings depending on callers, and compatibility sensitivity for hash inputs. Test signals should cover normal framing, multiple strings with positions, required trailer success/failure, truncated strings, bad comma, zero-length strings, and golden hash/extension fixtures.
