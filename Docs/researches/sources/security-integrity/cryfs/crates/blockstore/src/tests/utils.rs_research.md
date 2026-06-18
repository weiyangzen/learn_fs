# sources/security-integrity/cryfs/crates/blockstore/src/tests/utils.rs

Purpose: This file provides deterministic test fixtures for blockstore tests. `blockid(seed)` derives a stable 16-byte `BlockId`, and `data(size, seed)` returns reproducible `Data` bytes.

Important APIs and flow: `data` uses `DataFixture::new(seed).get(size).into()`. `blockid` uses the deterministic bytes from `data(16, seed)` and parses them as a `BlockId`.

State and persistence: The helpers are pure and have no persistence. Their role is to make stored block contents and ids stable across runs, implementations, and assertion points.

Dependencies and integration: The module depends on `cryfs_utils::data::Data`, `DataFixture`, and crate `BlockId`. It is used heavily by low-level conformance tests to avoid hand-written byte fixtures.

Risks and test signals: Because ids are generated from pseudo-random fixture bytes, tests cover realistic opaque identifiers while remaining deterministic. Any change in `DataFixture` output would affect many expected block ids indirectly.
