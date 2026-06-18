<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/db_options.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/db_options.rs

## Purpose
`db_options.rs` wraps tirocks DB options so the rest of `engine_tirocks` can pass around a single `RocksDbOptions` type for either standard RocksDB or Titan DB configurations.

## Important APIs, Types, and Functions
`RocksDbOptions` wraps an `Options` enum containing `DbOptions` or `TitanDbOptions`. It exposes `env`, `is_titan`, `into_rocks`, and `into_titan`, and implements `Default`, `Deref`, and `DerefMut` to common `RawDbOptions`.

## Control Flow
Accessors dispatch based on the enum variant. Conversion methods consume `self` and panic if the wrong variant is requested.

## State and Persistence Behavior
This is pre-open configuration state. Titan versus Rocks variant determines the DB type opened by tirocks and therefore storage feature behavior.

## Dependencies and Integration Points
It depends on tirocks env and option types. Utility/opening code uses `is_titan`, `env`, and `into_*` to decide how to create DBs.

## Risks and Edge Cases
Variant mismatch panics are acceptable for internal wiring but risky if exposed to untrusted configuration paths. Unlike `cf_options.rs`, there is no public `default_titan` constructor in this file, so Titan DB creation depends on other module paths.

## Test Signals
Tests should cover default Rocks options, env propagation through both variants, mutable raw option access, and wrong-variant panic behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/db_options.rs -->
