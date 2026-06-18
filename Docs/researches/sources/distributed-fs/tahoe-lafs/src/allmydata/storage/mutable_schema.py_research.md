# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/mutable_schema.py

## Purpose
Defines versioned on-disk schemas for mutable share containers. It generates recognizable 32-byte magic headers, constructs an empty mutable header, binds each schema version to the right lease serializer, and identifies a schema from bytes read from an existing share.

## Important APIs, Types, And Functions
`_magic(version)` builds the fixed 32-byte header marker. Version 1 preserves a historical five-byte suffix; later versions derive the suffix with `tagged_hash()`. `_header()` writes the fixed container header, four blank lease slots, and the initial extra-lease count. `_Schema` holds `version`, `lease_serializer`, and `_magic`, with `for_version()`, `magic_matches()`, and `header()`. Exports include `ALL_SCHEMAS`, `ALL_SCHEMA_VERSIONS`, `NEWEST_SCHEMA_VERSION`, and `schema_from_header()`.

## Control Flow
New share creation calls `NEWEST_SCHEMA_VERSION.header(nodeid, write_enabler)`, which produces an empty data region and points the extra-lease offset just past the fixed lease area. Existing share loading passes header bytes to `schema_from_header()`, which scans supported schemas and returns the one whose magic matches.

## State And Persistence
The schema determines immutable header bytes, write-enabler placement, the starting extra-lease offset, and whether lease secrets are cleartext or hashed through `lease_schema`. Constants `_HEADER_FORMAT`, `_HEADER_SIZE`, and `_EXTRA_LEASE_OFFSET` encode layout assumptions shared with `MutableShareFile`.

## Dependencies And Integration Points
Depends on `LeaseInfo().mutable_size()`, `tagged_hash()`, and the v1/v2 mutable lease serializers. It is consumed by `MutableShareFile.is_valid_header()`, constructor validation, and share creation.

## Risks And Test Signals
Schema detection is prefix based, so magic uniqueness is essential. Layout constants must remain synchronized with `mutable.py`; otherwise new shares can be unreadable or leases can overlap data. Tests should verify 32-byte magic strings, version uniqueness, v1/v2 recognition, blank lease initialization, extra-lease count placement, and that unsupported headers produce `UnknownMutableContainerVersionError` in the share layer.
