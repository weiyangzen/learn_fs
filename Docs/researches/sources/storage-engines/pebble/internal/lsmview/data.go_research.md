# sources/storage-engines/pebble/internal/lsmview/data.go

## Purpose
This file defines the JSON data contract for generating an external LSM visualization. It is a small schema package used by code that wants to describe Pebble levels, tables, key boundaries, and table details in a compact form.

## Important APIs, Types, And Functions
`Data` is the root document with `Levels []Level` and `Keys []string`. `Level` names a displayed LSM level and contains `Tables []Table`. `Table` carries a string label, byte size, integer indexes into `Data.Keys` for smallest and largest keys, and a list of detail strings. The JSON tags define the public wire shape: `level_name`, `tables`, `label`, `size`, `smallest_key`, `largest_key`, and `details`.

## Control Flow
There is no executable control flow. The code is a set of Go structs whose tags are consumed by `encoding/json`, most directly by `GenerateURL` in `url.go`.

## State, Persistence, And Side Effects
The schema is immutable by convention but not enforced by the type system. State is serialized into JSON and then embedded into URL fragments by the companion encoder. The `SmallestKey` and `LargestKey` fields are indexes, not duplicated key strings, so correctness depends on callers keeping `Keys` sorted and the table indexes valid.

## Dependencies And Integration Points
The file has no imports. It integrates with `url.go`, with any Pebble code that transforms manifest/version metadata into diagram data, and with the external `raduberinde.github.io/lsmview/decode.html` viewer expected to understand this JSON shape.

## Risks And Edge Cases
The types do not validate key-index bounds, key order, level order, or whether table key spans are coherent. A caller can create a `Table` whose indexes are out of range or reversed. Because the schema is part of a URL payload contract, changing JSON field names is a compatibility risk for existing viewers and tests.

## Test Signals
Coverage comes indirectly from `url_test.go`, which constructs a `Data` value and asserts that `GenerateURL` emits the expected compressed URL. There are no data-only tests for schema validation because the schema intentionally has no validators.
