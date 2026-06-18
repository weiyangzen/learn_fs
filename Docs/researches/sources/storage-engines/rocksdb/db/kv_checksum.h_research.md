# sources/storage-engines/rocksdb/db/kv_checksum.h

## Purpose

`kv_checksum.h` implements lightweight, non-persistent protection tokens for individual key/value entries as they move through RocksDB internals. The `ProtectionInfo...` template classes represent XORs of independently seeded hashes over selected fields: key (`K`), value (`V`), operation/value type (`O`), sequence number (`S`), and column-family id (`C`).

The goal is to detect accidental corruption, field swaps, or mismatched metadata across internal transformations without imposing a persistent wire format. The file explicitly notes that integer fields are hashed in native byte order, so generated values are endianness-dependent and should not be stored as durable data.

## Important APIs, types, and functions

- `ProtectionInfo<T>` is the base token, with `GetStatus()`, `ProtectKVO()`, `ProtectKV()`, private `Encode()`, `Verify()`, and value accessors.
- `ProtectionInfoKVO<T>` represents a token that includes key, value, and op type. It can `StripKVO()`, `ProtectC()`, `ProtectS()`, update individual K/V/O fields, encode, and verify.
- `ProtectionInfoKVOC<T>` extends KVO with column-family id. It can `StripC()`, update K/V/O through the KVO member, update C, encode, and verify.
- `ProtectionInfoKVOS<T>` extends KVO with sequence number. It can `StripS()`, update K/V/O through the KVO member, update S, encode, and verify.
- `ProtectionInfoKV<T>` protects only key and value and supports encode/verify.
- Aliases `ProtectionInfo64`, `ProtectionInfoKVO64`, `ProtectionInfoKVOC64`, and `ProtectionInfoKVOS64` provide the common 64-bit form.
- Seed constants `kSeedK`, `kSeedV`, `kSeedO`, `kSeedS`, and `kSeedC` intentionally differ by a large odd increment to reduce swapped-field collisions.

## Control flow

A caller starts with default `ProtectionInfo<T>` value zero. Calling `ProtectKVO()` or `ProtectKV()` XORs the current token with seeded non-persistent hashes of the selected fields and returns a more specific protection type. `ProtectC()` and `ProtectS()` add column-family id or sequence number respectively. `Strip...()` methods apply the same hashes again to remove fields, returning to a less-specific type; after all protected fields are stripped, `GetStatus()` returns `OK` only if the value is back to zero.

Update methods support in-place transformations without fully stripping and re-protecting. For example, `UpdateK(old_key, new_key)` XORs out the old key hash and XORs in the new key hash. Slice and `SliceParts` overloads allow callers to protect contiguous and fragmented key/value representations.

`Encode(len, dst)` writes the low `len` bytes of the token using fixed-width little-endian encoders for 2/4/8 byte lengths, or a single byte for length 1. `Verify(len, checksum_ptr)` decodes the stored bytes and compares against the low bits of the current token.

## State and persistence behavior

Each protection class is intended to be exactly the size of `T`, enforced with `static_assert` in constructors. State is only the current XOR value. The template assumes unsigned integer types up to 64 bits, and truncates hash values when `T` is narrower than 64 bits.

Protection values are non-persistent. They depend on native byte order for integer fields such as `ValueType`, `SequenceNumber`, and `ColumnFamilyId`, and are based on `NPHash64`, which is suitable for in-process protection rather than stable storage checksums.

## Dependencies and integration points

The file depends on `db/dbformat.h` for `ValueType`, encoding helpers, and sequence types, `rocksdb/types.h` for `ColumnFamilyId`, and `util/hash.h` for `NPHash64`, `GetSliceNPHash64`, and `GetSlicePartsNPHash64`.

It integrates with write batch processing, memtable/table builders, compaction, and other internal paths that need to carry and verify per-entry protection across representation changes. The class names encode which fields are currently covered, giving compile-time structure to legal protect/strip transitions.

## Risks and edge cases

- This is not a cryptographic checksum. XOR composition can miss paired errors that cancel out, and narrower `T` values reduce detection strength.
- Integer hashing is endian-dependent, so encoded protection values must not be persisted or compared across architectures.
- `Encode()` and `Verify()` assert that `len <= sizeof(T)` and support only 1, 2, 4, or 8 byte lengths.
- The code uses `reinterpret_cast<char*>` on integer fields for hashing native memory bytes. Changes to type size or representation affect computed values.
- Correctness relies on callers applying update/strip operations with exactly the old and new field values. A wrong old value will make later verification fail or, in rare collision cases, falsely pass.

## Test signals

Relevant tests should cover KVO, KVOC, KVOS, and KV flows; `Slice` and `SliceParts` equivalence; update methods matching strip/re-protect behavior; encode/verify lengths; status returning corruption for mismatches; and intentional field swaps. Endianness non-persistence should be documented rather than tested as a stable cross-platform value.
