# sources/sync-backup/borg/src/borg/legacy/upgrade.py

Purpose: upgrades Borg 1.2 archive items, compressed chunk payloads, and archive metadata into Borg 2.0-compatible forms during transfer.

Important APIs/types: `UpgraderFrom12To20` holds cache/args context. `new_archive` resets `HardLinkManager`. `upgrade_item` handles legacy hardlink master/slave metadata, source-to-target symlink conversion, field whitelisting, removal of obsolete keys, size computation, and `REQUIRED_ITEM_KEYS`. `upgrade_compressed_chunk` translates legacy compression/obfuscation metadata. `upgrade_archive_metadata` normalizes archive-level fields.

Control flow/state: hardlink slaves reuse remembered chunks and update cache stats. Chunk upgrade detects legacy zlib or prefixed compression, strips old prefixes, handles `ObfuscateSize` header byte order and padding, and fills `ctype`, `clevel`, `csize`, and `psize`. Metadata upgrade adds UTC offset to legacy timestamps and converts argv lists to command strings.

Dependencies/integration: uses `HardLinkManager`, legacy hardlink predicates, `Item`, compression classes, `CH_BUZHASH`, and `join_cmd`. Output feeds modern archive writing.

Risks: hardlink processing depends on seeing masters before slaves or having contentless semantics. Whitelisting can drop legacy fields. Compression conversion is byte-layout-sensitive. Unknown compression level is encoded as `0xFF`.

Test signals: hardlink master/slave cases, symlink conversion, field dropping, obfuscation payload conversion, legacy zlib conversion, chunker param normalization, timestamp suffixing, and command-line conversion.
