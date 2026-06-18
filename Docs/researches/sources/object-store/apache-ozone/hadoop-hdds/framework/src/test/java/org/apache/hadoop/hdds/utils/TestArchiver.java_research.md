<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java

Purpose: tests archive buffer-size selection and hard-link-based inclusion of files into tar archives.

Important APIs/types/functions: `Archiver.getBufferSize`, `Archiver.linkAndIncludeFile`, `TarArchiveOutputStream`, `TarArchiveEntry`, `Files.createLink`, Mockito static mocking, and argument capture.

Control flow: parameterized tests check minimum, proportional, and maximum buffer-size behavior for file sizes. The successful hard-link test creates a temp file, invokes `linkAndIncludeFile`, verifies tar archive entry interactions and copied byte count, and ensures temporary link cleanup. The failure test statically mocks `Files.createLink` to throw, then expects the method to surface the IOException and avoid archive inclusion.

State and persistence behavior: uses temporary directories/files and hard links. Successful flow creates and removes a link file under the temp dir; failure flow verifies no hard link remains.

Dependencies and integration points: integrates Ozone archiver helper with Apache Commons Compress tar output, Java NIO hard links, and Mockito `MockedStatic`.

Risks: hard-link behavior can be filesystem/platform-sensitive. Static mocking of `Files` must be tightly scoped to avoid impacting other tests. Archive entry metadata must match actual file size.

Test signals: asserts buffer-size bounds, bytes-copied equals source size, archive entry name/size, put/close archive calls, link cleanup, propagated IOException message, and no hard link creation on failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestArchiver.java -->
