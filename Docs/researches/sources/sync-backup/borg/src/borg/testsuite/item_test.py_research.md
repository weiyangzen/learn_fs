# sources/sync-backup/borg/src/borg/testsuite/item_test.py

Purpose: tests Borg `Item` typed property behavior, serialization dictionary shape, file-size derivation, opaque pointer roundtrip, and chunk-content comparison.

Important APIs and control flow: tests cover empty item membership/get/attribute errors, construction from bytes or string keys, invalid inputs, keyword construction, int property type checks, msgpack timestamp conversion for `atime`, surrogateescaped string properties for non-UTF-8 paths, list and `StableDict` properties, rejection of unknown attributes, `get_size` with and without `memorize`, `to_optr`/`from_optr`, and `chunks_contents_equal` across equal chunk boundaries, exhaustion, mismatch, and prefix cases.

State and persistence: in-memory `Item` internal dict state and typed property descriptors. `memorize=True` persists computed `size` inside the item.

Dependencies and integration points: depends on `borg.item.Item`, `chunks_contents_equal`, `ChunkListEntry`, `StableDict`, and msgpack `Timestamp`. `Item` is central to archive metadata, extraction, and legacy upgrade.

Risks: unknown-key rejection protects metadata schema. Surrogateescape path handling is important for round-tripping non-UTF-8 filesystem names.

Test signals: exact `as_dict` output, typed exceptions, timestamp wrapper conversion, size calculation, optr identity, and symmetric chunk comparison results.
