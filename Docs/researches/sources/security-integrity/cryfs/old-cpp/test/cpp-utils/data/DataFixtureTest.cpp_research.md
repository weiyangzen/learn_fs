# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureTest.cpp

Purpose: Tests deterministic data fixture generation for different sizes and seeds. It ensures fixtures can create empty, one-byte, and larger buffers and that seeded generation is stable.

Important APIs and types: Uses `cpputils::Data`, `DataFixture`, and GoogleTest through a `DataFixtureTest` fixture.

Control flow: Tests request fixture data of different sizes and seeds, compare repeated generation with the same seed, and compare different seeds for inequality.

State and persistence behavior: In-memory buffers only. The deterministic pseudo-random generator state is implicit in fixture construction and seed input.

Dependencies and integration points: Provides confidence for many other tests that rely on `DataFixture` as reproducible binary input.

Risks: Tests assert deterministic behavior, so changing the generator algorithm is a compatibility change even if callers only require stable size. Different-size determinism is covered by selected examples, not all sizes.

Test signals: Correct sizes, stable bytes for repeated seed/size pairs, and different bytes for distinct seeds.
