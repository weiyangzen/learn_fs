# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataTest.cpp

Purpose: Tests `FixedSizeData<N>` equality, inequality, copy/assignment behavior, conversion/storage behavior, and object-size expectations.

Important APIs and types: Uses `FixedSizeData`, `Data`, `DataFixture`, parameterized GoogleTest fixtures, and helper comparisons such as `EXPECT_DATA_EQ`.

Control flow: Tests build fixed-size buffers from deterministic fixtures or binary/string parameters, copy and assign them, compare expected bytes, and assert source data is unchanged.

State and persistence behavior: All data is in-memory fixed-size byte storage. No files are persisted.

Dependencies and integration points: Fixed-size data is foundational for cryptographic identifiers and serialized binary values where size must be compile-time enforced.

Risks: The lightweight-object assertion locks in layout/performance assumptions. Parameter coverage is representative, not exhaustive for every possible size.

Test signals: Exact byte equality/inequality, copy and assignment preserving source, expected fixed object size, and successful conversion with `Data`.
