# sources/sync-backup/casync/src/calocation.h

## Purpose
Defines the public `CaLocation` model used to identify positions in casync archive serialization and to track the filesystem origin of data.

## Important APIs, Types, and Functions
`CaLocationDesignator` distinguishes entry, payload, filename, goodbye, and void locations. `CaLocationWith` selects optional comparison/format fields. `struct CaLocation` stores reference count, path/designator/offset, optional size/root, freshness metadata, feature flags, archive offset, name table, and cached formatting. Public functions cover create/copy/ref/unref, format/parse, size/root patching, advancing, merging, opening, ID hashing, and equality.

## Control Flow
The header declares immutable-style operations: modifications take `CaLocation **` so implementations can copy when shared.

## State and Persistence Behavior
The struct is public and can represent both persisted string form and in-memory root/name-table attachments. `UINT64_MAX` marks unspecified optional numeric fields.

## Dependencies and Integration Points
Includes `cachunkid.h`, `cadigest.h`, `cafileroot.h`, `canametable.h`, and `util.h`. It is the bridge between encoder seek points, cache keys, and source-file reopening.

## Risks
Public mutable fields can bypass copy-on-write invariants. Callers must treat relative path and optional-field sentinels consistently with parser/formatter rules.

## Test Signals
ABI compile checks, designator validation, formatter/parser tests, equality masks, and integration through encoder seek locations cover this header.
