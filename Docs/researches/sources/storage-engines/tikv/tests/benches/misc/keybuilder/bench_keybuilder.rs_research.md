# sources/storage-engines/tikv/tests/benches/misc/keybuilder/bench_keybuilder.rs

## Purpose
This module benchmarks TiKV key construction helper paths.

## Important APIs, Types, and Functions
`gen_rand_str` creates random byte vectors with `thread_rng().fill_bytes`. `bench_key_builder_data_key` measures `keys::data_key` after cloning a 64-byte key. `bench_key_builder_from_slice` measures `KeyBuilder::from_slice`, `set_prefix`, and `build`.

## Control Flow
Each `#[bench]` prepares a random key outside the measured loop, then repeatedly constructs encoded/data keys inside the loop.

## State and Persistence Behavior
State is local random input only. No persistence.

## Dependencies and Integration Points
It depends on nightly `test`, `rand`, `keys::data_key`, and `tikv_util::keybuilder::KeyBuilder`.

## Risks and Test Signals
The benchmark includes allocation/cloning costs in the data-key case. It is a microbenchmark signal for key encoding helper overhead.
