# sources/storage-engines/tikv/components/test_pd/src/lib.rs

## Purpose
This crate root exposes the mock PD server test library. It imports TiKV logging macros, declares `mocker`, `server`, and `util` modules, and re-exports the core extension trait and server wrapper.

## Important APIs And Integration Points
`pub mod mocker` exposes mocker implementations and the `PdMocker` trait. `mod server` contains the gRPC server implementation. `pub mod util` contains client-construction helpers. `pub use self::{mocker::PdMocker, server::Server};` makes the primary testing surface available to downstream tests.

## State And Risks
The root itself owns no state. The `#[macro_use] extern crate` declarations are legacy-style macro imports for `tikv_util` and `slog_global`; removing or modernizing them could affect logging macro availability in submodules.

## Test Signals
Compile failures here generally indicate module/API export breakage across test code that imports `test_pd::Server` or `test_pd::PdMocker`.
