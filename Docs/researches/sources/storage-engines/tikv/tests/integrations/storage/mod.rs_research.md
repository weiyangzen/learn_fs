# sources/storage-engines/tikv/tests/integrations/storage/mod.rs

## Purpose
This module file wires the TiKV storage integration-test suite into Rust's test module tree. It has no runtime logic of its own, but controls which sibling test files are compiled and run.

## Important APIs, Types, and Functions
It declares `mod test_raft_storage;`, `mod test_raftkv;`, `mod test_region_info_accessor;`, `mod test_storage;`, and `mod test_titan;`.

## Control Flow
Compilation includes each listed submodule, allowing their `#[test]` and `#[bench]` items to register with the Rust harness.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no state or persistence. The dependency is purely module inclusion. The main risk is omission: adding a new storage integration file without updating this module would leave tests uncompiled. The signal is indirect through the included modules' tests.
