# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Schemas.h

## Purpose
`Schemas.h` declares symbolic keys for JSON schema documents used by status and management API surfaces. It centralizes schema key references so producers and validators can agree on schema identities.

## Important APIs, Types, And Functions
- `JSONSchemas` contains static `KeyRef` declarations for status, cluster configuration, latency band configuration, data distribution stats, log health, storage health, aggregate health, management API error, and fault tolerance status schemas.

## Control Flow And State
There is no runtime control flow in the header. Definitions in the corresponding implementation provide the actual key values.

## Persistence And External State
The static `KeyRef` values likely identify schema text or schema records elsewhere in the client/status system. This header itself has no mutable state.

## Dependencies And Integration Points
It depends on Flow and FDB key types. It integrates with JSON status generation, management API errors, and schema validation or publication code.

## Risks And Edge Cases
Because only declarations are present, mismatches between declarations and implementation definitions will be link-time or runtime integration problems. Schema key changes can break clients expecting stable schema names.

## Test Signals
Tests should verify that all declared schema refs are defined, non-empty where expected, stable across releases unless intentionally changed, and used by status/management code consistently.
