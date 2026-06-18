# sources/storage-engines/tikv/components/codec/Cargo.toml

## Purpose
Defines the TiKV `codec` component crate and its dependencies for byte/number/buffer encoding helpers.

## Important APIs, Types, And Functions
- Package `codec`, version `0.0.1`, edition 2021, unpublished Apache-2.0 crate.
- Runtime dependencies include `byteorder`, `error_code`, `libc`, `static_assertions` with nightly feature, `thiserror`, and workspace `tikv_alloc`.
- Dev dependencies include workspace `bytes`, `panic_hook`, `protobuf`, and `rand`.

## Control Flow
No executable control flow. The manifest selects dependencies used by codec modules and tests.

## State And Persistence Behavior
No state is stored in the manifest.

## Dependencies And Integration Points
The codec crate is a low-level component used by TiKV storage/encoding layers. `static_assertions` nightly feature aligns with low-level type/layout checks elsewhere.

## Risks And Edge Cases
Codec is foundational; dependency changes can affect serialization compatibility, allocation behavior, or panic/error integration. The manifest has no feature gating for buffer unsafe APIs.

## Test Signals
Tests live in source modules such as `buffer.rs`; dev dependencies support randomized buffer tests and protobuf codec coverage.
