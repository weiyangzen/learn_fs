# sources/storage-engines/tikv/tests/benches/misc/util/mod.rs

Purpose: module shim for misc utility benchmarks.

Important APIs and functions: declares `mod slice_compare;`.

Control flow: compile-time inclusion only.

State and persistence: none.

Dependencies and integration: wires slice comparison microbenchmarks into the misc bench tree.

Risks and test signals: module removal silently drops utility benches.
