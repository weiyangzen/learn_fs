# sources/storage-engines/tikv/tests/integrations/mod.rs

Purpose: root module for TiKV integration tests. It enables nightly test features, selects TiKV's custom test runner, imports `tikv_util` macros, and wires all integration-test submodules into one crate.

Important APIs and declarations: crate attributes enable `test`, `box_patterns`, and `custom_test_frameworks`; `#![test_runner(test_util::run_tests)]` routes execution through the shared TiKV test harness. Module declarations include backup, config, coprocessor, import, pd, raftstore, resource metering, server, encryption, and storage areas.

Control flow: Rust's test discovery compiles this module tree, and each child module exposes its own `#[test]` or macro-generated tests. There is no runtime logic beyond module registration.

State and persistence: no local persistence. State is created by child modules through test clusters, temporary directories, RocksDB engines, mock PD servers, and failpoints.

Dependencies and integration points: acts as the integration point between Cargo's test crate and all TiKV integration domains. The custom runner is a key dependency because it controls test filtering, failpoint setup, logging, and thread handling.

Risks: adding or removing a `mod` declaration changes which integration tests compile and run. The nightly feature gates mean toolchain drift can break the whole integration test crate before any individual test executes.

Test signals: successful compilation and discovery of all child modules is the primary signal. Runtime pass/fail is delegated to the child files.
