# sources/sync-backup/borg/src/borg/testsuite/legacy_upgrade_test.py

Purpose: tests `UpgraderFrom12To20`, converting Borg 1.2 item/archive/chunk metadata into Borg 2-compatible shapes.

Important APIs and control flow: helpers create an upgrader with mock cache/archive and legacy `Item` objects. Item-upgrade tests verify regular pass-through with required keys, whitelist stripping of obsolete fields, removal of `user=None`/`group=None`, symlink `source` to `target`, hardlink master `hlid` creation, hardlink slave `hlid`/chunk reuse from the master, cache `reuse_chunk` calls, and required-key presence. Archive-metadata tests convert `cmdline` and `recreate_cmdline` lists to strings, append UTC offset to naive times, convert 4-tuple chunker params to `(CH_BUZHASH, ...)`, preserve 5-tuples, override when rechunking, drop recreate fields, set empty tags, and omit absent optionals. Compressed-chunk tests promote raw legacy zlib metadata, strip explicit two-byte ctype/clevel prefixes for non-zlib, and upgrade Borg 1 obfuscation headers by extracting big-endian packed compressed size into metadata while preserving padding.

State and persistence: in-memory metadata and mocked cache/archive stats only. The upgrader carries hardlink master mapping during one archive.

Dependencies and integration points: depends on `UpgraderFrom12To20`, `Item`, compression classes/constants, `REQUIRED_ITEM_KEYS`, `CH_BUZHASH`, `ObfuscateSize`, zlib, struct packing, and argparse `Namespace`. It integrates with legacy archive import/migration.

Risks: hardlink slave handling depends on seeing masters before slaves. Chunk compression upgrade is byte-layout-sensitive for Borg 1 headers and obfuscation trailers.

Test signals: expected upgraded item dict keys, cache reuse call, archive metadata fields, promoted compression metadata, and preserved/stripped payload bytes.
