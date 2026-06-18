# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/error.py

## Purpose

This module defines shared exception types for Tahoe-LAFS crypto helpers.

## Important APIs, Types, And Functions

`BadSignature` indicates a signature did not match. `BadPrefixError` indicates an encoded key or byte string lacked an expected prefix.

## Control Flow

There is no control flow beyond class definitions.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

`ed25519.py`, `rsa.py`, and `util.py` raise these exceptions to provide Tahoe-local error names independent of cryptography internals.

## Risks

The exceptions carry no structured fields. Callers that need detail must inspect messages or wrap errors themselves.

## Test Signals

Tests should assert invalid signatures map to `BadSignature` and bad key prefixes map to `BadPrefixError`.
