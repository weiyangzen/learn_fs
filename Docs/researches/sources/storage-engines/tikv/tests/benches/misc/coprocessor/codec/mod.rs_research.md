# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mod.rs

## Purpose
This module benchmarks low-level table key prefix checks in TiDB/TiKV codec helpers.

## Important APIs, Types, and Functions
Benchmarks compare `starts_with(TABLE_PREFIX)`, manual first-byte table-prefix checks, `starts_with(RECORD_PREFIX_SEP)`, manual two-byte checks, and big-/little-endian `u16` prefix comparisons.

## Control Flow
Each `#[bench]` performs 1000 repeated checks inside the measured iteration with `black_box` to reduce optimization.

## State and Persistence Behavior
No state beyond fixed byte slices and local prefix values.

## Dependencies and Integration Points
It depends on nightly `test`, `byteorder`, and `tidb_query_datatype::codec::table` constants. It is included by `misc/coprocessor/mod.rs`.

## Risks and Test Signals
The benchmark is micro-architectural and sensitive to compiler optimization. It is a signal for choosing cheap prefix-check idioms, not functional correctness.
