# sources/storage-engines/tikv/src/coprocessor/statistics/mod.rs

## Purpose
Declares the statistics submodules used by the legacy coprocessor analyze path.

## Important APIs, Types, and Functions
Exports `analyze`, `analyze_context`, `cmsketch`, `fmsketch`, and `histogram` as public modules. There are no local functions or data types.

## Control Flow
No runtime control flow exists in this file. Its effect is compile-time module wiring.

## State and Persistence Behavior
No state is stored here. Persistence behavior belongs to child modules and any protobuf structures they produce.

## Dependencies and Integration Points
Integrates TiKV's coprocessor statistics package into the crate namespace so callers can reference `coprocessor::statistics::*` modules. It directly enables histogram, count-min sketch, FM sketch, and analyze logic to be compiled and exported.

## Risks and Edge Cases
Renaming or removing a module here breaks downstream imports and feature composition. Because this is a module barrel, risk is mostly accidental API-surface change.

## Test Signals
No direct tests. Coverage comes from tests in child modules such as `histogram.rs` and from higher-level analyze tests.
