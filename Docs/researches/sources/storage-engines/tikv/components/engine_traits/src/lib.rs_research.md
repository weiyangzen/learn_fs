# sources/storage-engines/tikv/components/engine_traits/src/lib.rs

Purpose: Documents and assembles the `engine_traits` crate, TiKV's generic storage engine abstraction with no concrete RocksDB dependency.

Important APIs and control flow: The large crate-level documentation explains capabilities, design notes, porting process, and refactoring rules. The module list exports extension traits for CF names/options, compaction, DB options, file system, flush, import, misc, snapshots, SST, write batches, MVCC/range/TTL/table properties, perf context, region cache, iteration, mutation, peeking, CF constants, engine pairs, errors, options, ranges, Raft engine traits, compaction jobs, raw TTL, and utilities. It also enables nightly features used by the crate.

State, persistence, and dependencies: No runtime state is held here, but exports define the public dependency boundary and prevent direct concrete-engine coupling.

Integration points, risks, and test signals: Every generic engine user imports through this crate. Risks include API sprawl, unstable Rust feature requirements, mismatched implementor modules, and public re-export churn. Test signals are workspace compilation and the `engine_traits_tests` crate that exercises the exported contracts.
