# sources/distributed-fs/tahoe-lafs/src/allmydata/test/web/matchers.py

## Purpose
This module defines a small testtools matcher adapter for treq/Twisted HTTP responses. It lets tests assert response status codes while preserving richer mismatch descriptions.

## Important APIs, Types, And Functions
`_HasResponseCode` is an `attrs` class with `match_expected_code`. Its `match(response)` method extracts `response.code`, delegates to the supplied matcher, and returns either `None` or a `Mismatch` with response context. `has_response_code(match_expected_code)` constructs the matcher.

## Control Flow
Callers pass a matcher such as `Equals(OK)`. `_HasResponseCode.match` compares the response's `code` field and wraps any mismatch detail from the delegated matcher.

## State And Persistence
The only state is the immutable expected-code matcher stored in `_HasResponseCode`. There is no persistence.

## Dependencies And Integration Points
It integrates `attrs`, `testtools.matchers.Mismatch`, treq response objects, and testtools assertion style. It is used by web log and private-resource tests.

## Risks And Test Signals
The matcher assumes the object under test has a `code` attribute. Its signal is narrow but useful: response-code failures include both the response object and delegated matcher details instead of a bare equality failure.
