# sources/storage-engines/tikv/src/storage/raw/mod.rs

## Purpose
This is the module boundary for raw-storage snapshot adapters and the public raw-store facade. It exposes encoded-value handling, raw MVCC projection, and `RawStore`.

## Important APIs, Types, and Functions
- `pub mod encoded` exports TTL/value decoding wrappers.
- `pub mod raw_mvcc` exports latest-version projection for API V2 raw MVCC keys.
- `mod store` keeps implementation details private.
- `pub use store::RawStore` makes `RawStore` the public entry point.

## Control Flow
There is no runtime control flow in this file. It determines which submodules are externally reachable and hides `store` internals except for the `RawStore` type.

## State and Persistence Behavior
No state is stored here. The persistence behavior lives in the submodules: encoded raw values, timestamped raw MVCC keys, and raw scan/checksum logic.

## Dependencies and Integration Points
Other storage code imports `storage::raw::RawStore` through this re-export. Tests and API-version-specific code may also import `storage::raw::encoded` and `storage::raw::raw_mvcc` directly.

## Risks
The main risk is API surface drift. Making `store` private while re-exporting `RawStore` is clean, but moving or renaming submodules affects downstream imports. Any new raw adapter module must be added here or it will not be visible.

## Test Signals
No direct tests are needed for this module declaration. Build failures and raw-storage integration tests are the useful signals.
