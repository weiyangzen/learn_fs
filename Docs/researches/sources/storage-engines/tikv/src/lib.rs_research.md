# sources/storage-engines/tikv/src/lib.rs

## Purpose
Crate root for the TiKV server library in this source tree. It defines crate-level docs, feature gates, macro imports, public modules, and version logging helpers.

## Important APIs, Types, and Functions
Public modules are `config`, `coprocessor`, `coprocessor_v2`, `import`, `read_pool`, `server`, and `storage`. `tikv_version_info` returns a formatted multiline version string using Cargo/build environment variables plus optional build time. `tikv_build_version` returns `CARGO_PKG_VERSION`. `log_tikv_info` logs a welcome message and each nonempty line of version info.

## Control Flow
At runtime, only the helper functions execute. Version info pulls compile-time env vars with fallbacks, trims feature text, and logs line by line. The rest is compile-time crate setup and module exposure.

## State and Persistence Behavior
No mutable state is stored here. Version helpers expose build metadata embedded at compile time and write to TiKV logs.

## Dependencies and Integration Points
Imports macros from `fail`, `serde_derive`, `more_asserts`, and `tikv_util`; enables several nightly Rust features. Public modules expose the researched coprocessor and import subsystems.

## Risks and Edge Cases
The crate depends on nightly features including `min_specialization`, `deadline_api`, and `type_alias_impl_trait`; compiler upgrades can affect build stability. Missing build env vars produce explicit fallback strings. Module visibility changes here have crate-wide API impact.

## Test Signals
No direct tests in this file. Version functions are simple but could be smoke-tested by asserting package version and fallback formatting. Most coverage comes from public child modules.
