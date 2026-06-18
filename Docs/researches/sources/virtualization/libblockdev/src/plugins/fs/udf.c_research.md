# File Research: sources/virtualization/libblockdev/src/plugins/fs/udf.c

Implements UDF filesystem support.

Key entry points:
- `bd_fs_udf_is_tech_avail()` checks support and dependencies.
- `bd_fs_udf_mkfs()` runs `mkudffs`.
- `bd_fs_udf_set_label()` uses `udflabel` and sets both logical volume identifier and volume identifier.
- `bd_fs_udf_set_uuid()` uses `udflabel --uuid`.
- `bd_fs_udf_get_info()` parses `udfinfo --utf8`.
- `bd_fs_udf_check_label()` and `_check_uuid()` validate UDF label and UUID formats.

Core mechanics:
- Dependencies are `mkudffs`, `udflabel`, and `udfinfo`.
- Check, repair, and resize are explicitly unsupported.
- `get_vid()` derives a valid UDF Volume Identifier from a label, truncating based on UDF character-width rules.
- Mkfs option generation maps label to `--lvid` plus derived `--vid`, UUID to `-u`, and preserves extra args.
- `bd_fs_udf_mkfs()` chooses block size from the caller or device logical block size via `BLKSSZGET`; defaults media type to `hd` and revision to `0x201`.
- Label validation distinguishes ASCII, valid UTF-8, and Unicode characters above U+00FF.
- UUID validation requires 16 lowercase hexadecimal characters.
- `parse_udf_vars()` parses `key=value` output from `udfinfo`, ignoring `start=` lines.
- Info extraction reads UDF revision, VID, LVID, block size, total blocks, free blocks, then adds UUID/label via common probing.

Important invariants:
- UDF logical volume labels can be up to 126 ASCII/compatible chars, but labels containing characters above U+00FF are limited to 63 chars.
- UDF VID is stricter than LVID and is truncated before being passed to tools.
- UUID randomization uses `udflabel --uuid=random`.
- No check/repair/resize path is advertised.

Filesystem/block relevance:
- Provides UDF creation, metadata labeling, UUID setting, and information query for optical/media-style and partition-table-capable filesystems.

Notable risks:
- UTF-8/VID truncation rules are subtle and may surprise callers expecting exact label round trips.
- `parse_udf_vars()` transfers split-string ownership into the hash table; changes here need careful memory handling.
- Info parsing depends on `udfinfo` key names.
