## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestScanTransientIOUtil.java

Purpose: Tests transient scan I/O classification, specifically "Too many open files" detection in exception messages and scan-error collections.

Important APIs/types/functions: `ScanTransientIOUtil.isTooManyOpenFiles`, `scanErrorsAreOnlyTooManyOpenFiles`, `MetadataScanResult.fromErrors`, `ContainerScanError`, and `FailureType`.

Control flow: Unit tests feed `FileSystemException`, `FileNotFoundException`, nested `IOException`, unrelated `IOException`, all-transient scan errors, mixed errors, and empty results into the utility and assert boolean classification.

State and persistence behavior: Pure classification tests. `File` instances are placeholders and not read.

Dependencies and integration points: Protects scanner behavior that should treat file-descriptor exhaustion differently from durable corruption or missing files.

Risks and test signals: Message matching can be platform-sensitive. The mixed-error test ensures transient-only classification is not broadened accidentally.
