# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopNestedDirGenerator.java

Purpose: Integration tests for Freon Hadoop nested directory generator command `ddsg`, validating generated nested directory depth and span through the Ozone filesystem.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `Freon.getCmd`, `OzoneClient`, `ObjectStore`, Hadoop `FileSystem`, `FileStatus`, and helpers `verifyDirTree`, `depthBFS`, and `spanCheck`.

Control flow: Per-test setup opens a cluster client and object store; cleanup closes it. The test invokes `verifyDirTree` with several depth/span combinations, including span zero. Each invocation creates a volume/bucket, runs `freon ddsg` against `o3fs://bucket.volume`, lists the root through Hadoop FS, computes depth with breadth-first traversal, then counts child directories at the last parent/leaf parent and compares with expected span.

State and persistence behavior: Creates Ozone volumes, buckets, and directory keys. The filesystem view is read after generation to validate namespace state.

Dependencies and integration points: Covers Freon nested directory generation, Ozone FS URI access, OM address configuration, and Hadoop filesystem directory listings.

Risks: `depthBFS` assumes at least one root status and uses the last visited path to check span. It validates structural shape but not naming or all branches exhaustively. Span zero has special path/depth handling.

Test signals: BFS-computed depth must equal expected depth, and `spanCheck` on the selected path must equal expected span.
