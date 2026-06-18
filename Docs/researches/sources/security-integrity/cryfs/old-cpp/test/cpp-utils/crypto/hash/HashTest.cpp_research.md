# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/crypto/hash/HashTest.cpp

Purpose: Tests salted hashing behavior in `cpp-utils/crypto/hash/Hash`. It verifies salt generation, deterministic hashing for identical data and salt, and changed outputs when data or salt differs.

Important APIs and types: Uses `Hash`, `DataFixture`, and GoogleTest. Test cases exercise salt generation and hash calculation over deterministic `Data` inputs.

Control flow: Each test creates fixture data and one or more salts, calls hash functions, and compares salts or digest outputs for equality or inequality.

State and persistence behavior: All state is in memory: generated salts, input buffers, and digest outputs. No keys or hashes are persisted.

Dependencies and integration points: Connects crypto hash utility code with the `Data` buffer abstraction and deterministic fixtures.

Risks: Indeterminism tests can theoretically collide, though probability should be negligible. These tests validate behavioral properties rather than known-answer vectors.

Test signals: Salt field preserved in hash output, same data/salt yields same digest, and different data or salt yields different digest.
