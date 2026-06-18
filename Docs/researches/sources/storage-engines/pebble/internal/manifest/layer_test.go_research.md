# sources/storage-engines/pebble/internal/manifest/layer_test.go

## Purpose
This small unit test verifies the public string representation of all normal `Layer` variants. It protects debugging, datadriven output, and error messages that rely on stable layer names.

## Important APIs And Functions
- `TestLayer` builds `Level(0)` through `Level(6)`, `L0Sublevel(0)` through `L0Sublevel(2)`, and `FlushableIngestsLayer`.
- It asserts `Layer.String()` returns `L0`, `L1`, `L0.0`, and `flushable-ingests` style values.

## Control Flow
The test iterates a fixed case table and runs each expected string as a subtest. Each subtest calls `String` once and compares with `require.EqualValues`.

## State And Persistence Behavior
There is no persistent state. The test only covers the in-memory layer value's presentation contract.

## Dependencies And Integration Points
It depends on the constructors in `layer.go` and `testify/require`. The checked strings appear in version debug output and ordering errors.

## Risks And Test Signals
The file does not test invalid constructor panics or accessor misuse. Its signal is narrow but important: changes to layer display names will be caught immediately.
