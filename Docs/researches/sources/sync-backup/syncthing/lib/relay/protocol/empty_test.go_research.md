# sources/sync-backup/syncthing/lib/relay/protocol/empty_test.go

## Purpose
Empty test file to include the relay protocol package in package test runs even without hand-written assertions.

## Important APIs, Types, and Functions
No APIs are defined.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Package declaration only. It provides compile-test participation for generated XDR code and packet definitions.

## Risks and Edge Cases
It does not validate wire compatibility or malformed packet handling. Behavioral coverage must come from other packages or future tests.

## Test Signals
`go test` compiles the relay protocol package; this file itself contributes no assertions.
