# sources/storage-engines/pebble/internal/manifest/layer.go

## Purpose
`layer.go` defines `Layer`, a compact descriptor for a logical section of the LSM: a whole level, an L0 sublevel, or the flushable-ingests layer above the LSM. It gives code that iterates or reports across levels/sublevels a single typed value instead of loose integer conventions.

## Important APIs, Types, And Functions
- `Layer` stores a `layerKind` and `uint16` value.
- `Level(level int)` constructs whole-level layers for L0 through L6 and panics on invalid levels.
- `L0Sublevel(sublevel int)` constructs a specific L0 sublevel, bounded by `uint16`.
- `FlushableIngestsLayer()` constructs the special ingest layer.
- `IsSet`, `IsFlushableIngests`, `IsL0Sublevel`, `Level`, `Sublevel`, `String`, and `SafeFormat` expose inspection and redaction-safe formatting.

## Control Flow
Construction validates inputs and stores a kind/value pair. Accessors branch on the kind and panic on invalid use, for example calling `Level` on flushable ingests or `Sublevel` on a non-sublevel. Formatting maps kinds to strings like `L4`, `L0.2`, and `flushable-ingests`.

## State And Persistence Behavior
`Layer` is in-memory identification state only. It is not a manifest record format; it is used to label table iteration, ordering checks, and logging/debug output.

## Dependencies And Integration Points
The file depends on `NumLevels`, CockroachDB errors, and redaction formatting. `Version.AllLevelsAndSublevels`, `Version.AllTables`, and `CheckOrdering` consume `Layer` values.

## Risks And Test Signals
The main risks are invalid layer construction and accidental misuse of level/sublevel accessors. Panics are deliberate invariant enforcement. `layer_test.go` locks down user-visible string output for levels, sublevels, and flushable ingests.
