# sources/storage-engines/rocksdb/util/hash128.h

Purpose: lightweight 128-bit hash declaration header separated from `hash.h` to avoid pulling `math128.h` into the common hash header.

Important APIs: declares `Unsigned128 Hash128(const char*, size_t, uint64_t seed)` and unseeded overload; provides `GetSliceHash128(const Slice&)`.

Control flow: `GetSliceHash128()` directly calls `Hash128()` with slice data/size.

State and persistence: no state. The declared hash is stable/persistent for non-cryptographic use.

Dependencies and integration: includes `rocksdb/slice.h` and `util/math128.h`; implemented in `hash.cc`.

Risks: consumers must treat it as non-cryptographic despite 128-bit width. Changes to implementation would affect persistent users.

Test signals: no direct test in this subset.
