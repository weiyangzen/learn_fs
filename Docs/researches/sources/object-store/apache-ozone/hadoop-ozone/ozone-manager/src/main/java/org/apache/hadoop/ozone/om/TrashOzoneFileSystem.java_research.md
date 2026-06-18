# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/TrashOzoneFileSystem.java

Purpose: `TrashOzoneFileSystem` is a minimal `FileSystem` implementation used by the OM trash emptier. It implements only the filesystem operations the trash policy needs and converts them into OM requests submitted through Ratis.

Important APIs and types: Implemented operations include `getUri`, `rename`, `delete`, `listStatus`, `getFileStatus`, `getTrashRoots`, `exists`, `mkdirs`, and working-directory methods. Unsupported file IO methods throw `UnsupportedOperationException`. Internal helpers build `RenameKey`, `DeleteKey`, and `DeleteKeys` `OMRequest` messages and submit them after `preExecute`.

Control flow: For FSO buckets, `rename` and `delete` send one recursive/atomic OM request for the path. For non-FSO buckets, `RenameIterator` and `DeleteIterator` list all keys under the path in batches, convert each key to an `OFSPath`, build per-key requests, and submit them. Listing uses OM metadata manager list APIs and batches with `OZONE_FS_ITERATE_BATCH_SIZE` and `OZONE_MAX_LIST_KEYS_SIZE`. `getTrashRoots` enumerates user trash roots from bucket/key metadata and filters existence.

State and persistence behavior: The class persists nothing directly. It mutates OM metadata through Ratis-submitted requests and increments OM trash metrics. `runCount` supplies monotonically increasing call IDs per instance, and `CLIENT_ID` is static.

Dependencies and integration points: It connects `TrashPolicyOzone` with `OzoneManager`, `OFSPath`, OM request classes, Ratis submission utilities, OM metadata list/status APIs, and user info from `UserGroupInformation`.

Risks and test signals: Non-FSO rename/delete is multi-request and can be partially applied if a later key request fails; errors inside iterators are logged but do not necessarily abort. Path parsing and trash-root equality checks are critical. Tests should cover FSO atomic rename/delete, OBS recursive iteration, batch boundaries, non-empty delete behavior, missing paths, trash root enumeration across users, metrics increments, and Ratis failure handling.
