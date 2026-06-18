## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyRenameRequestWithFSO.java

**Purpose:** Extends single-key rename tests to FSO layout, validating parent directory table updates, open-file rename rejection, invalid path handling in preExecute, and normalization of unnormalized paths.

**Important APIs/types/functions:** Uses `OMKeyRenameRequestWithFSO`, `OMFileRequest.getDirectoryInfo`, `OmDirectoryInfo`, `OmKeyInfo`, `OmUtils.normalizeKey`, `OzoneConsts.HSYNC_CLIENT_ID`, and FSO `getOzonePathKey`. Overrides parent setup, key table insertion, request factory, DB key computation, and modification-time assertions.

**Control flow:** Setup creates distinct source and destination parent directories under the bucket object ID, inserts both in the directory table, and creates a source file under the source parent. Inherited success path renames the file. Additional tests mark the source as open via hsync metadata and expect `RENAME_OPEN_FILE`, assert invalid from/to names throw during preExecute, and verify repeated slash paths are normalized.

**State and persistence behavior:** Successful FSO rename moves a file row between parent object IDs and updates modification times on both source and destination parent directories, not just the file. DB keys use volume ID, bucket ID, parent object ID, and leaf key name.

**Dependencies and integration points:** Integrates rename with FSO directory metadata, hsync/open-file metadata, and path normalization. Depends on random object IDs from `getOmKeyInfo`, shared bucket object IDs, and directory-table rows created before validate/update.

**Risks:** Risks include allowing open hsync files to be renamed, failing to update parent directory modification times, normalizing source/destination in the wrong fields, and using object-store key names in FSO DB keys.

**Test signals:** `RENAME_OPEN_FILE`, thrown `OMException` for invalid names, normalized request fields, inherited OK rename assertions, and parent directory modification time equality are the main signals.
