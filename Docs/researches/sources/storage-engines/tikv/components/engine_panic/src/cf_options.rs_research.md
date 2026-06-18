# sources/storage-engines/tikv/components/engine_panic/src/cf_options.rs

Purpose: Provides panic stubs for column-family option access and mutation.

Important APIs and types: `PanicEngine` implements `CfOptionsExt` with associated `PanicCfOptions`. `PanicCfOptions` implements `CfOptions`, exposing write buffer, L0 trigger, pending compaction limit, block cache, Titan options, auto-compaction, SST partitioner, and compaction-thread controls.

Control flow and state: All methods panic and store no options. The file is a trait-surface checklist for real engines.

Dependencies and integration: References `engine_traits::{CfOptions, CfOptionsExt, SstPartitionerFactory}` and `PanicTitanDbOptions`.

Risks: It compiles only as long as the skeleton tracks the trait exactly; runtime use is invalid.

Test signals: No tests; trait compilation is coverage.
