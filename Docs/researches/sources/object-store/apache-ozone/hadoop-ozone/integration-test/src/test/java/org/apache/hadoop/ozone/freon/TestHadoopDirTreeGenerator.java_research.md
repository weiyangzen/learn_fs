# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopDirTreeGenerator.java

Purpose: Integration tests for Freon Hadoop directory tree generator command `dtsg`, validating generated directory depth, span, file count, and file size through the Ozone Hadoop filesystem.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `Freon.getCmd`, `OzoneClient`, `ObjectStore`, `BucketArgs`, `BucketLayout`, `OzoneFileSystemTestUtils.setPageSize`, Hadoop `FileSystem`, `FileStatus`, and `StorageSize`. Helpers include `verifyDirTree`, `traverseToLeaf`, and `verifyActualSpan`.

Control flow: Per-test setup opens an Ozone client; cleanup closes it. The parameterized test runs for `FILE_SYSTEM_OPTIMIZED` and `LEGACY` bucket layouts and verifies several volume/bucket trees with different depth, span, file count, and per-file-size combinations, including page-size-plus-half span. `verifyDirTree` creates the volume and bucket, invokes `freon dtsg` with root `o3fs://bucket.volume`, then lists the filesystem with a small page size. It checks root span, recursively follows one directory path to the leaf, validates intermediate span counts, validates leaf file sizes, and ensures duplicate names are not seen in a directory.

State and persistence behavior: Creates real volumes, buckets, directories, and files in the test cluster. The Hadoop filesystem listing reflects OM namespace state for both bucket layouts. Page size configuration affects listing pagination behavior.

Dependencies and integration points: Covers Freon CLI, Ozone object store bucket layout variants, Hadoop Ozone filesystem URI handling, OM address injection, directory listing pagination, and file size generation.

Risks: The traversal follows the first directory path rather than exhaustively validating all branches. Listing order may affect which path is checked, though span/file assertions still catch many regressions. The duplicate-name assertion message is awkward but functional.

Test signals: Expected depth, subdirectory span, file count, and file length must match for each scenario and bucket layout.
