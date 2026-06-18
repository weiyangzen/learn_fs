# sources/storage-engines/tikv/components/test_pd_client/src/lib.rs

## Purpose
This crate root exposes the in-memory test PD client implementation.

## Important APIs And Integration Points
It imports TiKV utility macros, declares the internal `pd` module, and re-exports all public items from it. Consumers can import `TestPdClient`, scheduling helper constructors, constants such as `INIT_EPOCH_VER`, and `bootstrap_with_first_region` directly from `test_pd_client`.

## State And Risks
The root owns no state. Its main risk is broad API exposure: because it re-exports the entire `pd` module, changes inside `pd.rs` can affect downstream tests directly.

## Test Signals
Compile failures at this root usually indicate module visibility, macro import, or re-export changes that break raftstore/storage tests.
