# sources/storage-engines/tikv/scripts/check-build-opts.py

## Purpose
Verifies that individual TiKV crates build with default features and test-engine feature combinations. It catches feature coupling hidden by workspace-wide builds.

## Important APIs and Control Flow
The script discovers crates from `components/` plus `cmd`, `tests`, and root `tikv`. It runs default `cargo check -p` and `cargo test -p --no-run`, then runs crates containing `test-engines-rocksdb` with `--no-default-features` and feature combinations for panic, RocksDB, and split KV/Raft engines. `run_and_collect_errors` records failing cargo commands and the script prints all failures before exiting 1.

## State, Dependencies, Integration
Only in-memory `errors` state is maintained. Cargo may write normal target/cache artifacts. Dependencies are Python 3.6+, Cargo, the TiKV workspace layout, and current feature naming conventions.

## Risks and Test Signals
Feature detection is string-based and can be fooled by comments or renamed features. It assumes repository-root execution and can be slow because it runs many cargo commands serially. Success is exit 0; failure output lists exact cargo commands for reproduction.
