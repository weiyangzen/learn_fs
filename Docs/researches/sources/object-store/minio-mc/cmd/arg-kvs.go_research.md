# sources/object-store/minio-mc/cmd/arg-kvs.go

## Purpose

`arg-kvs.go` defines a small ordered key-value collection used by command argument wrappers.

## Important APIs, Types, and Functions

`argKV` stores a JSON-serializable key and value. `argKVS` is a slice with methods `Empty`, `Set`, `Get`, and `Lookup`.

## Control Flow

`Set` scans for an existing key and replaces it in-place; if missing, it appends a new entry. `Get` delegates to `Lookup` and returns an empty string for absent keys. `Lookup` performs a linear scan.

## State and Persistence Behavior

State is in-memory only. JSON tags make the structures suitable for output or serialization by callers, but this file does not persist them.

## Dependencies and Integration Points

There are no external dependencies. It is a package-level utility for command code that needs simple ordered key-value state.

## Risks and Edge Cases

Lookups are O(n), which is fine for small argument lists but not large maps. Empty string values are indistinguishable from missing keys when using `Get`; callers needing that distinction must use `Lookup`.

## Test Signals

Tests should cover empty state, append and overwrite behavior, duplicate prevention through `Set`, and `Get` versus `Lookup` semantics.
