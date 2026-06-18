# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataTest.cpp

Purpose: Broad behavioral test suite for `cpputils::Data`, the dynamic byte buffer abstraction. It covers copy isolation, zero initialization/filling, move construction/assignment, equality/inequality, large sizes, file loading, and allocator ownership.

Important APIs and types: Uses `Data`, `DataFixture`, `SerializationHelper`, `TempFile`, fstreams, GoogleMock, and a `MockAllocator` fixture to validate allocation/free calls.

Control flow: Tests construct buffers from sizes, fixtures, files, and allocators; mutate copies; move buffers; store/load bytes; and compare content. Parameterized fixtures exercise size and string/binary inputs.

State and persistence behavior: Mostly in-memory buffer ownership. File-based tests use temporary files to verify load/store behavior and cleanup through `TempFile`.

Dependencies and integration points: Critical for crypto, serialization, and blockstore code that depend on `Data` byte ownership and move semantics.

Risks: Allocator tests are sensitive to exact ownership transfer timing. Large-size tests must avoid excessive memory in constrained environments.

Test signals: Correct byte contents, zero-filled buffers, equality results, file bytes, expected allocator calls, and no double-free after moves.
