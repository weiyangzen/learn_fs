<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/cf_options.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/cf_options.rs

## Purpose
`cf_options.rs` adapts tirocks column-family options to `engine_traits::CfOptions` and `TitanCfOptions`, allowing one wrapper to hold either standard RocksDB CF options or Titan CF options.

## Important APIs, Types, and Functions
`RocksCfOptions` wraps an internal `Options` enum: `Rocks(CfOptions)`, `Titan(TitanCfOptions)`, or temporary `None`. Public helpers include `is_titan`, `default_titan`, `into_rocks`, and `into_titan`. `Deref`/`DerefMut` expose common `RawCfOptions`.

Trait implementations expose max write-buffer number, L0 triggers, pending compaction byte limits, target file size, auto-compaction, disable-write-stall, and Titan min-blob-size conversion.

## Control Flow
`set_min_blob_size` converts a `Rocks` option into `Titan` by temporarily replacing the enum with `None`, converting tirocks options, setting the blob size, and storing the Titan variant. Accessors dispatch by enum variant. Several trait methods intentionally panic because the tirocks adapter has not implemented block-cache management, Titan option copying, or SST partitioner support.

## State and Persistence Behavior
The wrapper is mutable configuration state used before DB open. Converting to Titan changes which kind of CF options will be passed to tirocks and can affect persisted storage layout through Titan blob settings.

## Dependencies and Integration Points
It depends on tirocks `CfOptions`, `TitanCfOptions`, and `RawCfOptions`, plus `engine_traits::{CfOptions, TitanCfOptions}`. DB open utility code consumes `into_rocks` or `into_titan`.

## Risks and Edge Cases
`TitanCfOptions::new`, block-cache getters/setters, `set_titan_cf_options`, and SST partitioner installation panic. Calling `into_rocks` on Titan or `into_titan` on Rocks panics. The temporary `None` variant must never be observed outside conversion. This file is a clear partial-implementation boundary.

## Test Signals
Coverage should assert standard option getters/setters, Titan conversion through `set_min_blob_size`, panic paths for unsupported APIs, and compatibility with tirocks DB open code.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/cf_options.rs -->
