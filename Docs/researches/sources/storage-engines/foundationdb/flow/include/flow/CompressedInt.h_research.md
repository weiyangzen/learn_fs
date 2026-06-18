# sources/storage-engines/foundationdb/flow/include/flow/CompressedInt.h

Purpose: defines an order-preserving compressed signed integer serialization wrapper.

Important APIs/types/functions: template `CompressedInt<IntType>` with `value` and `serialize(Ar&)`.

Control flow: deserialization reads a sign/unary-length header, inverts bytes for negative encodings, reconstructs value bytes, and reinverts negative values. Serialization flips negative values, writes nonzero value bytes, computes bit length and encoded length, sets sign/unary header bits, optionally bit-flips the encoded bytes for negatives, and writes bytes through `ar.serializeBytes`.

State/persistence: encoded form is persisted by archives; wrapper stores one integer value in memory.

Dependencies/integration: depends on archive serializer APIs and integer byte operations. Used where sorted binary encodings of signed integers are needed.

Risks: assumes `IntType` supports signed comparison to zero; unsigned instantiations may behave unexpectedly. The GCC diagnostic suppression hints at compiler warning sensitivity around buffer manipulation. Boundary values need careful testing.

Test signals: round-trip serialization tests, bytewise ordering tests for negative/zero/positive values, and max/min integer coverage.
