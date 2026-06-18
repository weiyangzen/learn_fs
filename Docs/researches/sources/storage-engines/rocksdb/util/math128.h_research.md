# sources/storage-engines/rocksdb/util/math128.h

Purpose: supplies RocksDB's `Unsigned128` abstraction and 128-bit extensions for math/coding helpers on platforms with or without native `__uint128_t`.

Important APIs/types/functions: defines `Unsigned128` as `__uint128_t` when available or a `{lo, hi}` struct otherwise. The fallback implements shifts, bitwise operators, comparisons, and conversion to <=64-bit integral types. Helper APIs include `Lower64of128`, `Upper64of128`, `Multiply64to128`, specializations of math helpers for `Unsigned128`, `IsUnsignedUpTo128`, `EncodeFixed128`, `DecodeFixed128`, and `EncodeFixedGeneric`/`DecodeFixedGeneric` specializations for 16/32/64/128-bit values.

Control flow: compile-time macros choose native or fallback representation. Fallback shifts split operations across lower and upper halves. `Multiply64to128` uses native multiplication when possible or manual 32-bit limb decomposition otherwise. Specialized bit helpers dispatch to the 64-bit helpers for each half and recombine. Fixed encoding writes lower 64 bits first, then upper 64 bits, matching little-endian fixed coding.

State and persistence behavior: no mutable global state. The fixed 128-bit encode/decode functions define an in-memory and persisted byte layout for callers that store 128-bit values. The fallback struct asserts it has exactly two `uint64_t` words of storage.

Dependencies/integration points: depends on `util/coding_lean.h` and `util/math.h`. Hashing, tests, and generic algorithms use it when they need 128-bit hash values, wide multiplication, or fixed-width 128-bit serialization.

Risks: `TEST_UINT128_COMPAT` can force the fallback path, so both native and fallback semantics must stay aligned. Shift operators mask shift counts by 127, which is intentional behavior but differs from undefined native oversized shifts. Generic encode/decode intentionally static-assert for unsupported sizes. `BitwiseAnd` overloads rely on casts to the smaller participating type.

Test signals: `hash_test.cc` tests `Unsigned128` bitwise operations, comparisons, shifts, popcount/parity helpers, reverse/endian behavior, `DownwardInvolution`, `Multiply64to128`, and fixed/generic encoding and decoding.
