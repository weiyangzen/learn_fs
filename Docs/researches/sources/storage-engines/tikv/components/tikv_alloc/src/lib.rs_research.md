# sources/storage-engines/tikv/components/tikv_alloc/src/lib.rs

## Purpose
This is the root of the allocator crate. It documents allocator policy, selects one backend implementation with cfg gates, re-exports the public allocator/stat/profiling API, and installs the selected global allocator.

## Important APIs, Types, and Control Flow
The crate enables nightly test features and `core_intrinsics`. `AllocStats` is `Vec<(&'static str, usize)>`. `error` and `trace` are public modules. The `imp` module is selected from `jemalloc.rs`, `tcmalloc.rs`, `mimalloc.rs`, `snmalloc.rs`, or `system.rs` depending on Unix, `fuzzing`, and feature flags. `pub use crate::{imp::*, trace::*}` exposes backend functions and memory tracing. `#[global_allocator] static ALLOC: imp::Allocator = imp::allocator();` installs the selected allocator.

The test-only `runner` enables ignored tests with messages prefixed by `#ifdef <VAR_NAME>` when the environment variable is present, which is used for profiling tests requiring `MALLOC_CONF`.

## State, Dependencies, and Integration
Linking this crate transitively causes TiKV binaries and tests to use the production allocator where supported. The crate intentionally centralizes jemalloc-specific code and presents stable functions even when selected backends are no-op for profiling.

## Risks and Test Signals
Feature selection is the biggest risk. The cfg layout can define multiple `imp` modules if multiple allocator features are enabled simultaneously on Unix; normal workspace configuration must avoid that. Fuzzing disables custom Unix allocators and falls back to system. Tests are backend-specific and routed through the custom runner.
