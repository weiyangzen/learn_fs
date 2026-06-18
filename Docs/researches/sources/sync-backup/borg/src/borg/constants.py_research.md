# sources/sync-backup/borg/src/borg/constants.py

Purpose: centralizes Borg protocol, repository, archive, chunking, cache, tar, tag, exit-code, and crypto constants used across the codebase.

Important APIs/types: defines item/archive key allowlists (`ITEM_KEYS`, `ARCHIVE_KEYS`) and required keys, repository object type labels (`ROBJ_*`), size and segment limits, listing limits, chunker names and default params, sparse chunk allocation codes, files-cache modes and timestamp tolerances, tar PAX header names, special tags, exit code bands, timestamp formats, KDF parameters (`PBKDF2_ITERATIONS`, `ARGON2_ARGS`, `ARGON2_SALT_BYTES`), key algorithms, `KeyBlobStorage`, `KeyType`, cache/repository tag names, and README content strings.

Control flow and state: no runtime control flow beyond class/constant definition. These values shape serialization, compatibility, CLI defaults, and security behavior elsewhere.

Dependencies and integration: imported broadly, often with `from ..constants import *`. `KeyBlobStorage` and `KeyType` are used by crypto key selection/storage; chunk constants feed arg parsing and chunker factories; `ROBJ_*` labels are used by repo object formatting/parsing; tar constants are consumed by tar export/import.

Risks: many values are part of on-disk or wire compatibility. Changes to object type labels, key type bytes, item/archive key sets, chunker defaults, or size limits can make repositories unreadable or alter deduplication. The comment on `ITEM_KEYS` and `ARCHIVE_KEYS` warns robust unpacking/rebuild logic requires completeness.

Test signals: broad regression suite should cover manifest/archive unpacking, repository object parsing, chunker default behavior, modern/legacy exit-code classification, key type dispatch, tar metadata, and cache behavior when constants are changed.
