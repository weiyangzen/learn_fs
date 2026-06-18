# sources/storage-engines/rocksdb/db_stress_tool/db_stress_gflags.cc

## Purpose

`db_stress_gflags.cc` is the command-line surface for RocksDB's `db_stress` binary when built with gflags. It declares hundreds of `FLAGS_*` knobs that drive stress-test workload mix, DB option plumbing, table format options, cache and blob settings, fault injection, crash-recovery verification, compaction/flush/ingestion APIs, transaction modes, remote compaction, MultiGet/MultiScan behavior, and multi-DB execution.

The file is mostly declarative, but it is a central integration contract: other stress-tool translation units consume these globals through `DECLARE_*` and use them to construct `Options`, `ReadOptions`, `WriteOptions`, stress workloads, listener behavior, expected-state tracking, and fault-injection settings.

## Important APIs, Types, and Functions

- `ValidateUint32Range()` rejects unsigned 64-bit flag values that must later fit into `uint32_t`. It is registered for flags such as `seed`, `blob_direct_write_partitions`, `subcompactions`, `num_iterations`, `ops_per_thread`, and `log2_keys_per_lock`.
- `RegisterDbStressBdwFlagValidators()` registers the validator for `FLAGS_blob_direct_write_partitions` from inside `ROCKSDB_NAMESPACE`, allowing Blob Direct Write validation to be called from the main stress setup code.
- `ValidateInt32Positive()` enforces nonnegative integer flags such as `reopen` and `kill_random_test`.
- `ValidateInt32Percent()` enforces percent flags in `[0,100]` for read, prefix, write, delete, range-delete, no-overwrite, and iterator workload ratios.
- `ValidatePrefixSize()` enforces `prefix_size` in `[-1,8]` for hash/prefix memtable configurations.
- The `DEFINE_*` declarations use defaults from RocksDB option classes so command-line defaults track RocksDB option defaults.
- `extern "C" bool RocksDbIOUringEnable() { return true; }` opts this binary into io_uring support when available.

## Control Flow and State Behavior

There is no runtime loop in this file. Its control flow is static initialization: gflags variables are defined before `main`, and selected validators are registered as static objects. If validation fails during flag parsing, gflags rejects the run before the stress test initializes.

Downstream state effects are indirect. `db_stress_test_base.cc` reads these flags while constructing DB options, registering listeners, building table factories, configuring caches/rate limiters/checksum factories, and deciding which optional operations are sampled. `db_stress_driver.cc` uses thread, verification, fault-injection, and multi-DB flags to orchestrate worker threads and helpers. `db_stress_shared_state.*` uses flags such as `seed`, `max_key`, `log2_keys_per_lock`, `column_families`, and expected-values settings to build the expected-state oracle and lock striping.

Several flags influence persistent artifacts: `expected_values_dir`, `sync_fault_injection`, `preserve_unverified_changes`, and `expected_state_trace_*` control expected-state and trace files; DB path flags control physical DB directories; blob/WAL/checksum/table-format/timestamp/temperature/manifest flags influence persisted RocksDB files and metadata; `num_dbs` changes path interpretation.

## Dependencies and Integration Points

The file depends on gflags compatibility macros, RocksDB public option classes, cache and backup headers, blob option types, and shared constants from `db_stress_common.h`. It is compiled only under `#ifdef GFLAGS`.

Integration includes `db_stress_test_base.cc`, `db_stress_driver.cc`, `db_stress_listener.h`, `db_stress_shared_state.*`, `db_stress_table_properties_collector.h`, and stress variants for batched/no-batched/transaction/CF-consistency workloads. `options_file` also interacts with RocksDB option parsing by making stress setup ignore flag values represented in the options file.

## Risks and Edge Cases

Many flags are declared as wide integer types but later cast to narrower option fields; validator coverage matters for avoiding truncation. Percent flags are individually bounded, but this file does not enforce a sum. Some cross-flag requirements are documented rather than enforced here, such as stable expected-state parameters across runs or `env_uri` versus `fs_uri`.

Release/debug differences matter for fault injection because read fault handling depends on debug-only sync-point behavior in `SharedState`. Static initialization order is a residual risk around validators and gflags globals.

## Test Signals

Primary signals are successful `db_stress` startup with flag parsing/validation, stress runs covering selected APIs, and absence of assertions from consumers. Targeted configurations include fault-injection crash-recovery runs with `expected_values_dir`, compaction and ingestion sampling runs, transaction modes, table-properties collector runs, blob/cache/tiered-cache combinations, and multi-DB runs through `num_dbs`.
