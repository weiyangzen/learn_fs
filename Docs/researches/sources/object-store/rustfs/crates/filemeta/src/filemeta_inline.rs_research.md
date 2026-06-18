# sources/object-store/rustfs/crates/filemeta/src/filemeta_inline.rs

## Purpose

This module defines `InlineData`, the compact persisted container for object data embedded inside metadata rather than stored as separate part files. It wraps a versioned byte buffer containing a msgpack map from string keys to binary values. Keys are typically version UUID strings, and values are inline object payloads.

## Important APIs, Types, and Functions

- `InlineData(Vec<u8>)` is cloneable, serializable, deserializable, and defaults to an empty buffer.
- `INLINE_DATA_VER` is the only supported on-buffer version, currently `1`.
- `new()`, `update()`, and `as_slice()` construct, replace, and expose raw bytes.
- `version_ok()` accepts empty data and versions in `1..=INLINE_DATA_VER`.
- `after_version()` returns the msgpack map bytes after the leading version byte.
- `entries()` returns the msgpack map length, or zero for empty/unsupported version buffers.
- `find(key)` scans the map and returns the matching binary value.
- `validate()` ensures the stored map can be decoded and that keys are non-empty.
- `replace(key, value)` updates or appends a key and rewrites the full buffer.
- `remove_key(key)`, `remove(Vec<Uuid>)`, and `remove_two(first, second)` remove entries by literal string key or UUID-hyphenated keys.
- Internal helpers `contains_key_by`, `remove_keys_by`, `remove_two_keys_by_bytes`, and `serialize` implement efficient scanning and whole-map rewrite.

## Control Flow

Read operations skip the first byte, decode the msgpack map length, iterate key/value pairs, and skip values by advancing the cursor by their binary length. `find()` materializes the key as UTF-8 only when comparing to the requested string; `contains_key_by()` compares raw key bytes and avoids allocation for misses.

Write operations are rebuild-based. `replace()` reads all existing entries into key/value vectors, substitutes the first matching key or appends a new entry, then calls `serialize()`. Removal paths first scan for a hit to avoid rewriting on misses, then rebuild all non-removed entries. If all entries are removed, the raw buffer is set to empty rather than an encoded empty map.

`serialize()` asserts key/value vector length equality, writes the version byte, writes a msgpack map length, then emits each string key and binary value.

## State and Persistence Behavior

The persisted bytes are `version-byte || msgpack-map<string, bin>`. Empty inline data is represented by an empty vector, not by a versioned zero-length map. The code preserves entry order during replacements/removals except when appending new keys at the end. UUID removal canonicalizes keys using lower-case hyphenated UUID strings, so stored keys must match that textual form.

## Dependencies and Integration Points

The module uses crate-local `Error`/`Result`, `rmp` decode/encode primitives, `serde` derives for outer struct serialization, `std::io::Cursor/Read`, and `uuid::Uuid`. It is exported by `lib.rs` and used by `FileMeta` and test fixtures to store/retrieve inline data and by version headers through the inline-data flag stored in `MetaObject.meta_sys`.

## Risks and Edge Cases

- `validate()` does not call `version_ok()`, so a non-empty buffer with an unsupported version byte will still be decoded from byte 1 as msgpack.
- Cursor advancement trusts declared msgpack string/bin lengths; malformed buffers return decode/read errors, but extreme lengths could allocate large key buffers in `replace`, `remove_keys_by`, and `find`.
- `serialize()` uses an `assert_eq!`, so internal misuse with mismatched vectors panics instead of returning an error.
- `remove(Vec<Uuid>)` does a linear scan over encoded removal keys for every stored key; large maps or large removal sets may be quadratic.
- Duplicate keys are not collapsed except that `replace()` updates every matching key's value while leaving duplicates present.

## Test Signals

The module has unit tests for a missing `remove_key()` preserving the raw buffer and for `remove_two()` removing exactly two UUID-keyed entries while keeping an unrelated entry findable.
