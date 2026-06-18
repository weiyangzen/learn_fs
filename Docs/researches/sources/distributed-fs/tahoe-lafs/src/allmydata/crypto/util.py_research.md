# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/util.py

## Purpose

This module provides a small shared utility for validating and stripping byte prefixes from encoded crypto values.

## Important APIs, Types, And Functions

`remove_prefix(s_bytes, prefix)` returns `s_bytes` without `prefix` when present, otherwise raises `BadPrefixError`.

## Control Flow

The function checks `s_bytes.startswith(prefix)`, slices on success, and raises with a message on failure.

## State And Persistence

There is no state or persistence.

## Dependencies And Integration Points

It depends on `BadPrefixError` and is used by Ed25519 parsing and client node ID handling to enforce Tahoe key prefixes.

## Risks

It assumes byte-like objects with `startswith()` and slicing. Error messages include `repr(prefix)` but not the input, avoiding accidental key disclosure.

## Test Signals

Cover successful removal, empty suffix, wrong prefix, and non-bytes misuse if callers rely on strict type behavior.
