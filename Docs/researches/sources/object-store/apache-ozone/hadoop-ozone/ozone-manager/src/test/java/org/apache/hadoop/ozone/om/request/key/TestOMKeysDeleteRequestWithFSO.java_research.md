## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeysDeleteRequestWithFSO.java

**Purpose:** Reuses batch delete assertions for FSO layout, deleting top-level directory paths that contain files.

**Important APIs/types/functions:** Uses `OmKeysDeleteRequestWithFSO`, `DeleteKeysRequest`, `DeleteKeyArgs`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

**Control flow:** The overridden setup creates three directories (`dir0`..`dir2`), each with one file row under the directory parent ID. It adds only the top-level directory path with trailing slash to the delete request/list. Success and failure tests instantiate the FSO batch delete class, then reuse base response checks; failure appends nonexistent `dummy`.

**State and persistence behavior:** FSO batch delete must resolve directory paths into directory/file table effects while the inherited checks verify requested top-level paths no longer resolve through the layout's key table view. The setup stores files with leaf key names and parent IDs.

**Dependencies and integration points:** Integrates batch delete with FSO recursive directory deletion and inherited response validation. It depends on FSO bucket setup and path trailing slash semantics for directories.

**Risks:** Risks include deleting only directory markers while leaving child files, incorrect handling of trailing slash directory names, partial-delete response mismatch, and inherited object-store assertions being too coarse for child table cleanup.

**Test signals:** OK or `PARTIAL_DELETE` response statuses, deleted valid paths, and reported `dummy` failure show batch FSO delete behavior.
