# sources/storage-engines/tikv/components/backup-stream/src/config.rs

## Purpose
`config.rs` provides online configuration management for backup-stream. It stores the current `BackupStreamConfig` and forwards validated changes to the backup-stream endpoint scheduler.

## Important APIs, Types, And Functions
- `BackupStreamConfigManager` holds a `Scheduler<Task>` and `Arc<RwLock<BackupStreamConfig>>`.
- `BackupStreamConfigManager::new` constructs the manager from scheduler and initial config.
- `impl ConfigManager for BackupStreamConfigManager` implements `dispatch(change)`.

## Control Flow
On config dispatch, the manager logs the change, takes a write lock, applies the `ConfigChange` through `OnlineConfig::update`, validates the resulting config, schedules `Task::ChangeConfig(cfg.clone())`, and returns success.

## State And Persistence Behavior
The current backup-stream config is kept in an `Arc<RwLock<_>>` shared with other components. Applying a change mutates this in-memory config before scheduling the endpoint task. Persistent config storage, if any, is handled by the wider online-config/server system, not this file.

## Dependencies And Integration Points
It integrates with `online_config::{ConfigChange, ConfigManager, OnlineConfig}`, TiKV `BackupStreamConfig`, `tikv_util::worker::Scheduler`, backup-stream endpoint `Task`, and server startup code that registers config managers for backup-stream.

## Risks And Edge Cases
- If `update` succeeds but `validate` fails, the in-memory config has already been mutated unless `OnlineConfig::update` is internally transactional.
- Scheduler failure returns an error after the config lock mutation, possibly leaving local config changed without endpoint application.
- The write lock is held while scheduling, so scheduler backpressure/errors happen inside the critical section.

## Test Signals
Router tests reference `BackupStreamConfigManager` and should cover config-change propagation. Direct unit tests for failed validation and scheduler failure would be useful because of mutation-before-schedule behavior.
