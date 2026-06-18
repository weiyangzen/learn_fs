# sources/storage-engines/tikv/tests/benches/misc/coprocessor/mod.rs

## Purpose
This module groups miscellaneous coprocessor benchmarks under the `misc` bench target.

## Important APIs, Types, and Functions
It declares `mod codec` and `mod dag`.

## Control Flow
Benchmark functions are supplied by child modules. This file only controls module inclusion.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `tests/benches/misc/mod.rs`, making codec and DAG expression microbenchmarks part of the misc target.

## Risks and Test Signals
The file's risk is limited to module path drift. Misc bench compilation confirms correctness.
