# sources/sync-backup/syncthing/lib/relay/client/empty_test.go

## Purpose
Empty package test file that ensures the relay client package participates in `go test` even when no ordinary test files exist.

## Important APIs, Types, and Functions
No functions or types are defined.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Package declaration only. It keeps the package testable and can host future tests without changing package metadata.

## Risks and Edge Cases
Provides no behavioral coverage. It can give a false impression that the package has tests when it only has compile coverage.

## Test Signals
`go test` compiles package and dependencies; no assertions run from this file.
