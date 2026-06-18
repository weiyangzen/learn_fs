# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfoGroup.java

Purpose: Represents one key version's block-location lists, grouped by block create version.

Important APIs/types/functions: Constructors accept a version plus list or map of `OmKeyLocationInfo`. Accessors expose latest-version-only blocks, all blocks, collection views, counts, and multipart flag. `getProtobuf`/`getFromProtobuf` convert to `KeyLocationList`. Package methods `generateNextVersion`, `appendNewBlocks`, `removeBlocks`, and `addAll` are used by `OmKeyInfo`.

Control flow and state: Constructors group list entries by each block's create version and ensure the group version has at least an empty list. `generateNextVersion` creates a map containing only new blocks at `version + 1`. `appendNewBlocks` stamps incoming blocks with the current version.

State and persistence behavior: Embedded inside persisted `OmKeyInfo` and multipart part metadata. Protobuf stores the group version, multipart flag, and flattened key-location list; deserialization regroups by create version.

Dependencies and integration points: Used by key versioning, block commit, multipart keys, and read/list responses.

Risks: `getLocationVersionMap` exposes the mutable internal map. HashMap iteration can make serialized key-location ordering non-deterministic unless callers use ordering-insensitive comparisons. Deprecated version-specific getter can return null-backed copies if the version is absent.

Test signals: Grouping by create version, protobuf round trip, append/new-version semantics, multipart flag persistence, count/list methods, and mutation exposure expectations.
