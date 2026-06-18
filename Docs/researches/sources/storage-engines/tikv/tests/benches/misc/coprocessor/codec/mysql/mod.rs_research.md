# sources/storage-engines/tikv/tests/benches/misc/coprocessor/codec/mysql/mod.rs

## Purpose
This module is a namespace wrapper for MySQL codec microbenchmarks.

## Important APIs, Types, and Functions
It declares `mod json`, exposing the JSON codec benchmark module to the misc benchmark tree.

## Control Flow
There is no runtime control flow beyond module inclusion by the Rust compiler.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It is included by `misc/coprocessor/codec/mod.rs` and pulls in `codec/mysql/json/mod.rs`.

## Risks and Test Signals
The main risk is module path drift. Compilation of the misc benchmark confirms inclusion remains valid.
