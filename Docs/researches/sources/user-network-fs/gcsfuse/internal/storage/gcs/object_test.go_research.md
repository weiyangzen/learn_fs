# sources/user-network-fs/gcsfuse/internal/storage/gcs/object_test.go

## Purpose
This file tests simple object predicates with ogletest.

## Important APIs and Control Flow
`TestObject` runs the ogletest suite. `ObjectTest` is registered in `init`. Tests cover positive and negative `MinObject.HasContentEncodingGzip`, finalized and unfinalized `MinObject`, and finalized and unfinalized full `Object`.

## State, Dependencies, and Integration
There is no persistent state. Dependencies include `testing`, `time`, and `ogletest`. The tests guard exact gzip matching and zero-time finalized semantics used by read/write behavior.

## Risks and Test Signals
The tests are intentionally narrow. They do not cover all metadata fields, only predicate semantics. Any future change that treats content encoding case-insensitively would require test and behavior updates.
