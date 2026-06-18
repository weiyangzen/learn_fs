# sources/storage-engines/pebble/example_test.go

## Purpose
Provides a package example for basic Pebble usage through the public API.

## Important APIs, Types, And Functions
`Example` calls `pebble.Open`, `DB.Set`, `DB.Get`, closer `Close`, and `DB.Close`, using `vfs.NewMem` and `pebble.Sync`.

## Control Flow
The example opens an in-memory DB, writes key `"hello"` with value `"world"`, reads it back, prints key and value, closes the value closer, and closes the DB. The `// Output:` block makes it an executable Go example.

## State And Persistence Behavior
State is held only in a memory filesystem. The write is synchronous with respect to the configured in-memory FS, and the read value remains valid until the returned closer is closed.

## Dependencies And Integration Points
This file is in package `pebble_test`, so it demonstrates external-package usage instead of privileged internals. It integrates with Go's example test runner and validates basic API ergonomics.

## Risks And Edge Cases
The example intentionally avoids advanced options, iteration, batches, and persistence to disk. It demonstrates the important closer lifetime on `Get`, which users must honor to release resources.

## Test Signals
The exact printed output `hello world` is checked by `go test`.
