## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMKeyDeleteRequestWithFSO.java

**Purpose:** Extends single-key delete coverage to FSO layout, adding tests for `OzonePrefixPathImpl`, recursive access checks, directory names containing colons, and deletion of a parent after child entries have been deleted in cache.

**Important APIs/types/functions:** Uses `OMKeyDeleteRequestWithFSO`, `OzonePrefixPathImpl`, `OzonePrefixPath`, `OzoneFileStatus`, `OmDirectoryInfo`, `OmKeyInfo`, FSO table helpers, and recursive `KeyArgs.setRecursive`. Overrides `addKeyToTable`, `getOmKeyDeleteRequest`, and `getBucketLayout`.

**Control flow:** The class seeds `c/d/e/file1` by creating parent directories and an FSO file row. Prefix-path tests instantiate viewers for directories and files, list children, and assert file/directory status. Recursive access tests build empty and file-containing directory trees and check whether recursive ACL checks are required. Delete tests execute FSO delete requests for files/directories and verify OK statuses.

**State and persistence behavior:** State spans `directoryTable`, `file/keyTable`, and delete cache entries. The parent-after-child test models Ratis double-buffer visibility by deleting child directory and file in cache, then deleting the parent before DB flush. Colon directory tests ensure path parsing does not confuse `:` with URI syntax in FSO buckets.

**Dependencies and integration points:** Integrates delete with FSO path traversal, ACL prefix path listing, directory emptiness checks, and cache-aware child existence helpers. Depends on `OMRequestTestUtils.addParentsToDirTable`, `addFileToKeyTable`, and `createOmDirectoryInfo`.

**Risks:** Risks are false "directory not empty" due to stale DB state after cached child deletes, recursive access not applied to non-empty directories, file paths treated as directories, colon names rejected incorrectly, and FSO DB key mismatch from leaf/full path confusion.

**Test signals:** Child iterator behavior, `isDirectory`/`isFile`, recursive-access booleans, OK statuses for deletes, and parent delete success after child deletes are the main behavioral signals.
