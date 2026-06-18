# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/package-info.java

## Purpose
Documents the package as containing block-token-related classes, though the text says "test classes" despite production token classes living here.

## Important APIs and types
No executable APIs. The package includes `ShortLivedTokenIdentifier`, `OzoneBlockTokenIdentifier`, and `OzoneBlockTokenSelector`.

## Control flow, state, and persistence
There is no runtime behavior.

## Dependencies and integration points
The package supports HDDS block token authentication for client-to-datanode operations.

## Risks and test signals
No direct tests. The package comment may be misleading and should be corrected if documentation cleanup is in scope.
