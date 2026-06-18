# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_content_type.py

## Purpose
This module tests MIME content type value objects used by testtools details.

## Important APIs, types, and functions
`TestContentType` validates `ContentType` constructor error handling, attributes, equality, and `repr()` formatting. `TestBuiltinContentTypes` validates built-in `UTF8_TEXT` and `JSON` constants.

## Control flow
Tests instantiate content types with and without parameters, compare equality outcomes, and check that repr sorts/quotes parameters deterministically.

## State and persistence behavior
No state persists. Objects are immutable-by-convention value objects with parameter dictionaries supplied at construction.

## Dependencies and integration points
It depends on `ContentType`, `JSON`, `UTF8_TEXT`, and matcher helpers. Content types are consumed by `Content`, stream attachment conversion, and result formatting.

## Risks and test signals
The exact `repr()` output is part of stream MIME metadata and diagnostic output. Parameter ordering must be stable for deterministic tests.
