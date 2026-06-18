# sources/object-store/garage/src/garage/cli/local/repair.rs

Purpose: runs offline metadata repair operations that need direct local Garage model access.

Important APIs/types/functions: async `offline_repair(config_file, secrets, opt)`.

Control flow: requires `--yes`, reads and secret-fills config, initializes `Garage::new`, then dispatches `OfflineRepairWhat` to recount K2V item counters or object counters. Logs progress and returns after repair.

State and persistence: opens and mutates local metadata stores by recounting counters from authoritative tables. It should be run with care because it bypasses remote admin RPC and works locally.

Dependencies and integration points: uses `garage_model::garage::Garage`, config/secrets helpers, and CLI structs. K2V branch is feature-gated.

Risks: requires correct config/secrets and should not be run casually on a live/incorrect node. The `--yes` guard prevents accidental invocation. Errors during `Garage::new` or recount abort the operation.

Test signals: no direct tests; repair table implementations should have their own coverage.
