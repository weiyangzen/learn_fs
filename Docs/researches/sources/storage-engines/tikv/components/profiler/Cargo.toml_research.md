# sources/storage-engines/tikv/components/profiler/Cargo.toml

Purpose: Defines the `profiler` crate, a small optional profiling helper for TiKV developers. It is not published and exists to expose zero-cost no-op functions by default and gperftools/Callgrind support when the `profiling` feature is enabled on Unix.

Important APIs/types/functions: The `profiling` feature enables optional dependencies `lazy_static`, `gperftools`, `callgrind`, and `valgrind_request`. The base dependency is `tikv_alloc`, ensuring the crate links TiKV allocation behavior. The `prime` example is declared with `required-features = ["profiling"]`.

Control flow: Cargo feature resolution selects whether `src/lib.rs` compiles `profiler_unix` or `profiler_dummy`. On non-Unix or without `profiling`, consumers still compile against the same public `start`/`stop` API but receive no-op behavior.

State and persistence behavior: No crate-level persistence is configured. When profiling is enabled, runtime output may be produced by gperftools into a profile file chosen by callers; that behavior is in `profiler_unix.rs`, not the manifest.

Dependencies and integration points: The manifest integrates external native/profiling crates only under Unix cfg and optional feature gates. This reduces normal build footprint and avoids requiring gperftools or valgrind-related dependencies for production builds.

Risks: Enabling `profiling` can introduce native dependency and platform availability issues. The example cannot be built unless all optional profiling dependencies resolve. Feature names are part of developer workflows, so changes must coordinate with documentation and scripts.

Test signals: Cargo validates the example under `profiling`. No tests are declared here; build matrix coverage should include default and `--features profiling` on Unix.
