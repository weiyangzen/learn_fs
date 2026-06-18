# sources/storage-engines/tikv/tests/integrations/config/dynamic/split_check.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/split_check.rs

Purpose: tests online coprocessor split-check config propagation.

Important APIs: `SplitCheckRunner`, `SplitCheckTask::Validate`, `SplitCheckConfigManager`, `CoprocessorHost`, `ConfigController`, `Module::Coprocessor`, and Rocks engine creation with `CF_DEFAULT` plus `split-check-config`.

Control flow: a temporary Rocks engine is created from `cfg.storage.data_dir`; `setup` starts a lazy split-check worker with a runner and registers its config manager. The test first sends an unrelated raftstore update and validates original coprocessor config, then updates `split_region_on_table`, `batch_split_limit`, and `region_split_keys`, validating the worker sees the constructed expected config.

State and persistence: runtime worker state and a temporary RocksDB are used; no config file persistence is involved. The worker is stopped.

Dependencies and integration points: raftstore coprocessor split logic, worker scheduler, online config. Risks include one-second validation timeout and CF naming assumptions. Test signal is equality of the live split-check config after updates.
