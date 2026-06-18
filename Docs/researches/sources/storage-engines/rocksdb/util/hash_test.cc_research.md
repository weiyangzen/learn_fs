# sources/storage-engines/rocksdb/util/hash_test.cc

Purpose: provides regression tests for RocksDB hash and small math primitives whose outputs are format-sensitive. It locks down legacy 32-bit `Hash`, XXH-derived `Hash64`/`Hash128`, range-reduction helpers, 128-bit coding helpers, and bit-manipulation utilities used by Bloom filters, table indexes, hash tables, and other persisted or performance-sensitive paths.

Important APIs/types/functions: tests call `Hash`, `Hash64`, `Hash128`, `Hash2x64`, `GetSliceHash64`, `GetSliceHash128`, `BijectiveHash2x64`, `BijectiveUnhash2x64`, `FastRange32`, `FastRange64`, `FastRangeGeneric`, `BottomNBits`, `FloorLog2`, `ConstexprFloorLog2`, `CountTrailingZeroBits`, `BitsSetToOne`, `BitParity`, `EndianSwapValue`, `ReverseBits`, `DownwardInvolution`, `BitwiseAnd`, `Multiply64to128`, `EncodeFixed128`, `DecodeFixed128`, `EncodeFixedGeneric`, and `DecodeFixedGeneric`.

Control flow: fixed-value tests first verify stable hash outputs for many short byte strings. Miscellaneous loops then compare seeded and unseeded hash entry points, check upper/lower reconstruction, assert seed and length sensitivity, and validate bijective 16-byte transformations. Descriptor helpers compress hash results for all lengths up to 430 bytes to guard against algorithm changes across XXH size classes. The math section runs templated bit-operation checks over many integral types and `Unsigned128`, then checks multiplication and fixed-width coding.

State and persistence behavior: the test itself persists nothing, but many expected values are contract tests for persisted file-format behavior, especially Bloom hash compatibility and encoded table metadata compatibility. The `main` function prints the `GetSliceNPHash64("RocksDB")` id for diagnostic visibility before running GoogleTest.

Dependencies/integration points: depends on `util/hash.h`, `util/hash128.h`, `util/math.h`, `util/math128.h`, `util/coding.h`, `util/coding_lean.h`, and RocksDB's test harness. It is the local test signal for both hash and math utility headers because math has no separate dedicated test binary in this subset.

Risks: expected hash descriptors are intentionally brittle; legitimate algorithm upgrades require coordinated format-compatibility review. Some negative uniqueness checks are probabilistic and could theoretically collide, though the chosen inputs make that unlikely. The templated math tests avoid undefined inputs such as full-width `BottomNBits` and zero `FloorLog2`, so callers still need to respect those preconditions.

Test signals: this file is itself the primary test. It covers stable hash schemas, `FastRange` boundary values, 32/64/128-bit bit operations, endian swap/reverse behavior, downward involution properties, 64x64-to-128 multiplication, and fixed-width generic encoding/decoding.
