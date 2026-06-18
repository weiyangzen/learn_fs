# sources/storage-engines/tikv/components/sst_importer/src/config.rs

Purpose: online-configurable importer settings and config manager.

Important APIs and types: `Config` contains `num_threads`, `stream_channel_window`, `import_mode_timeout`, and `memory_use_ratio`; `OnlineConfig` derive enables online updates except skipped fields. `ConfigManager` wraps `Arc<RwLock<Config>>` and a weak pointer to a resizable runtime pool.

Control flow: defaults are 8 threads, stream window 128, import-mode timeout 10 minutes, memory ratio 0.3. `validate` repairs zero thread/window values to defaults and rejects memory ratios outside `[0.0, 0.5]`. `dispatch` clones current config, applies an `online_config::ConfigChange`, validates it, adjusts runtime thread count if the pool still exists, and stores the new config.

State and persistence behavior: in-memory config under RwLock. Runtime thread pool size can be changed live. Persistence, if any, is handled by the surrounding TiKV config controller.

Dependencies and integration points: imported by `sst_importer` and import-mode switchers. Uses `online_config`, `tikv_util::config::ReadableDuration`, `ResizableRuntime`, and `HandyRwLock`.

Risks: skipped fields cannot be updated online. Invalid memory ratios reject dispatch, while zero thread/window silently repair during validation. Runtime adjustment only happens if the weak pool upgrades.

Test signals: direct tests are outside this file in importer config/update paths; `sst_importer.rs` tests reference invalid config and thread update behavior.
