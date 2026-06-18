# sources/storage-engines/pebble/internal/lsmview/url_test.go

## Purpose
This file verifies that `GenerateURL` produces a deterministic LSM viewer URL for a representative `Data` payload.

## Important APIs, Types, And Functions
`TestGenerateURL` constructs a `Data` value with two levels, four tables, ordered boundary keys, table labels, sizes, key indexes, and details. It calls `GenerateURL`, checks that no error is returned, and compares `url.String()` against a fixed expected URL.

## Control Flow
The test is straightforward: arrange a fixture, call the encoder, trim whitespace from the expected multiline string, and assert exact equality. The fixture comments document the intended key-index relationships for human readers.

## State, Persistence, And Side Effects
The test has no durable state and does not perform network access. It only checks the local string representation of the URL. Because the expected fragment contains compressed binary data represented as base64, the test is sensitive to every byte of the encoding pipeline.

## Dependencies And Integration Points
The test depends on `strings.TrimSpace`, Go testing, and `testify/require`. It integrates with `data.go` and `url.go`, and indirectly with Go's JSON encoder, zlib implementation, base64 URL encoding, and `net/url.String`.

## Risks And Edge Cases
The exact-string assertion is useful but brittle. Semantically equivalent changes, such as a different compression level, raw base64 encoding, or JSON encoding without a trailing newline, will fail the test. The fixture does not validate viewer behavior, URL length limits, empty levels, duplicate keys, or invalid table indexes.

## Test Signals
Passing this test signals that the current URL contract for a normal multi-level LSM diagram is stable. A failure usually indicates a deliberate or accidental wire-format change that must be coordinated with the external viewer and any consumers of generated links.
