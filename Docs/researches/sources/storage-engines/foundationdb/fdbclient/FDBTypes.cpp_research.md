# sources/storage-engines/foundationdb/fdbclient/FDBTypes.cpp

## Purpose

`FDBTypes.cpp` implements small but shared fdbclient type utilities for key ranges, key selectors, key-value-store type names, and perpetual storage wiggle locality parsing/matching. These helpers sit below higher-level transaction and storage configuration code and encode behavior that must stay compatible with FoundationDB key-size limits and configuration strings.

## Important APIs, types, and functions

- Key range utilities:
  - `toPrefixRelativeRange(KeyRangeRef range, Optional<KeyRef> prefix)` converts an absolute range into a prefix-relative range, returning `allKeys` boundaries where the absolute boundary is outside the prefix.
  - `keyBetween(const KeyRangeRef& keys)` returns a compact key at or near the range end, capped by `CLIENT_KNOBS->SPLIT_KEY_SIZE_LIMIT`, useful for split keys.
  - `randomKeyBetween(const KeyRangeRef& keys)` attempts to produce a deterministic-random key strictly inside a non-empty, non-single-key range, falling back to `keys.end` if no valid interior key can be produced.
- Key selector methods:
  - `KeySelectorRef::setKey()` truncates oversized keys to a maximum legal key-selector representation using `getMaxKeySize()`.
  - `KeySelectorRef::setKeyUnlimited()` stores a key without truncation.
  - `KeySelectorRef::toString()` renders selectors in first-greater/first-greater-or-equal/last-less/last-less-or-equal form based on `offset` and `orEqual`.
- Description overloads:
  - `describe(const std::string&)` returns the string as-is.
  - `describe(const UID&)` returns `UID::shortString()`.
- Store type mapping:
  - `KeyValueStoreType::getStoreTypeStr()` maps enum values to storage engine strings such as `ssd-2`, `ssd-redwood-1`, `ssd-rocksdb-v1`, `ssd-sharded-rocksdb`, `memory`, and `memory-radixtree`.
  - `KeyValueStoreType::fromString()` parses accepted names and aliases such as `ssd` and `redwood`, throwing `unknown_storage_engine()` for unknown input.
- Perpetual storage wiggle locality:
  - `ParsePerpetualStorageWiggleLocality()` parses semicolon-separated `key:value` locality filters, with `"0"` meaning no filters.
  - `localityMatchInList()` returns true if any parsed key/value pair matches a `LocalityData` value.

## Control flow

`toPrefixRelativeRange()` has a simple three-way behavior: no prefix returns the original range; prefixed boundaries have the prefix stripped; non-prefixed begin/end boundaries widen to `allKeys.begin` or `allKeys.end`.

`keyBetween()` scans common bytes between `begin` and `end` until a differing byte or `SPLIT_KEY_SIZE_LIMIT`. If a differing byte is found, it returns the end prefix through that byte. If begin is a prefix of a longer end and one more byte is allowed, it returns one more end byte; otherwise it returns `end`.

`randomKeyBetween()` first handles empty or single-key ranges by returning `end`. If `begin` is shorter than `end`, it appends a random byte constrained by the corresponding `end` byte. Otherwise it finds the first differing byte, tries to mutate a later non-`0xff` byte upward, then tries to choose a byte between the differing begin/end bytes, then appends a byte if key-size limits allow, finally returning `end` when no interior key is possible.

`KeyValueStoreType::fromString()` uses a static map and throws when the string is absent. `getStoreTypeStr()` uses a switch and returns `"unknown"` for unexpected enum values.

`ParsePerpetualStorageWiggleLocality()` asserts the input passes `isValidPerpetualStorageWiggleLocality()`, treats `"0"` as an empty match list, splits on `;`, then splits each item on `:` into `Optional<Value>` key/value pairs. `localityMatchInList()` scans those pairs and checks `LocalityData::get(key) == value`.

## State and persistence behavior

This file has no persistent state and does not access disk or FoundationDB keys. The only static runtime state is the local `names` map in `KeyValueStoreType::fromString()`. Random key generation uses `deterministicRandom()`, so it participates in FoundationDB's deterministic simulation behavior rather than external nondeterminism.

## Dependencies and integration points

The file includes `fdbclient/FDBTypes.h`, `fdbclient/Knobs.h`, `fdbclient/NativeAPI.actor.h`, and Boost string splitting. It depends on client knobs for key-size and split-key limits, `LocalityData` for locality matching, `UID` formatting, FoundationDB `KeyRef`/`KeyRangeRef`/`ValueRef` arena-backed string types, and the error factory `unknown_storage_engine()`.

Storage engine string mapping is an integration point for configuration and process/storage initialization. Locality parsing is used by perpetual storage wiggle configuration to target storage processes by locality fields. Key/range utilities are shared primitives for splitting, selector rendering, and prefix-range calculations.

## Risks and edge cases

- `randomKeyBetween()` has several fallback paths that return `keys.end`, so callers must tolerate the result not being strictly inside the range for empty, single-key, or saturated key-space cases.
- The branch where `begin.size() < end.size()` reads `end[begin.size()]`; this relies on `begin < end` and the size relation to make that index valid.
- `KeySelectorRef::setKey()` truncation is intentional but can surprise callers comparing stringified selectors to original oversized input.
- `KeyValueStoreType::getStoreTypeStr()` returns `"unknown"` for default enum cases, while `fromString()` throws for unknown strings. Round-trip behavior is therefore only guaranteed for known enum values.
- `ParsePerpetualStorageWiggleLocality()` uses `ASSERT` validation rather than returning an error, so invalid strings are expected to be rejected before calling it or will abort in assert-enabled contexts.
- Parsed `ValueRef` objects reference bytes from `localityKeyValues.c_str()`. Because they are stored as `Optional<Value>` rather than `Optional<ValueRef>`, this should deep-copy into owned values; preserving that ownership property is important if the type changes.

## Test signals

This file contains inline unit tests:

- `/KeyRangeUtil/randomKeyBetween` validates interior-key generation for prefix and non-prefix ranges and verifies the no-interior-key fallback for `q` to `q\x00`.
- `/KeyRangeUtil/KeyRangeComplement` validates subtracting subranges from a parent range across middle, outside, overlapping-left, overlapping-right, and covering cases.
- `/PerpetualStorageWiggleLocality/Validation` validates accepted and rejected locality filter strings, including multi-filter and `"0"` cases.
- `/PerpetualStorageWiggleLocality/ParsePerpetualStorageWiggleLocality` validates parsed key/value pairs and matching behavior against `LocalityData`.

Additional useful tests would cover `toPrefixRelativeRange()`, `keyBetween()` at `SPLIT_KEY_SIZE_LIMIT`, key selector truncation/string rendering, and storage engine string aliases/error behavior.
