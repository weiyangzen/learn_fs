# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMSetTimesRequestWithFSO.java

Purpose: specializes set-times coverage for `BucketLayout.FILE_SYSTEM_OPTIMIZED`, covering both files and directories. It extends `TestOMSetTimesRequest`, overrides key creation and request construction, and adds a directory timestamp test.

Important APIs and types: `OMKeySetTimesRequestWithFSO`, `OMFileRequest.getOMKeyInfoIfExists`, `OzoneFileStatus`, `OmKeyInfo`, `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `getOzonePathKey`. Constants model `c/d/e/file1` where `c/d/e` is the parent directory and `file1` is the stored leaf name.

Control flow: `addKeyToTable` creates parent directory rows, builds `OmKeyInfo` for `FILE_NAME` with object ID and parent object ID, writes it to the FSO key table, and returns the path-key. `testKeySetTimesRequest` sets mtime on `c/d/e/file1`, verifies `OMFileRequest` resolves a file status, and ensures the stored key name is the leaf `file1`. `testDirSetTimesRequest` changes `keyName` to the parent directory and validates directory status and mtime behavior.

State and persistence behavior: FSO resolution spans directory table and key table. The request must update the `OmKeyInfo` or `OmDirectoryInfo` resolved from path components rather than treating the full key string as the stored file name. Negative mtime again leaves the previous value unchanged.

Dependencies and integration points: uses the same `executeAndReturn` flow from the base class, but wraps requests with `OMKeySetTimesRequestWithFSO` and returns FSO bucket layout. It depends on the metadata manager’s volume and bucket numeric IDs for FSO key construction.

Risks covered: directory timestamp updates can be skipped if request code only searches key table; full path can be incorrectly persisted as file name; parent object IDs can be mishandled; negative mtime can overwrite valid timestamps. The test focuses on cache-visible metadata and not final DB batch mechanics.

Test signals: resolved `OzoneFileStatus` is non-null and is directory/file as expected, mtime equals the positive value after update, remains unchanged after `-1`, and key-table row keeps leaf file name.
