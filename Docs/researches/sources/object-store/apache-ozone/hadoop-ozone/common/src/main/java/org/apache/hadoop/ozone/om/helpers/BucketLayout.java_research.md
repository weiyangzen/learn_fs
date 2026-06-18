# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketLayout.java

Purpose: Enumerates OM bucket namespace layouts: `FILE_SYSTEM_OPTIMIZED`, `OBJECT_STORE`, and `LEGACY`.

Important APIs/types/functions: `fromProto` and `toProto` convert to Ozone Manager protobuf values. `isFileSystemOptimized`, `isLegacy`, `isObjectStore`, and `shouldNormalizePaths` encapsulate layout behavior. `fromString` defaults blank values to `LEGACY`. `validateSupportedOperation` rejects non-legacy layouts for older client operations.

Control flow and state: Stateless enum methods. Legacy behavior depends on the `enableFileSystemPaths` flag: with filesystem paths disabled, legacy buckets behave like object-store buckets.

State and persistence behavior: Stored in bucket metadata protobuf and controls key table/path normalization semantics after deserialization.

Dependencies and integration points: Used by `OmBucketInfo`, multipart abort info, request validation, and upgrade compatibility logic.

Risks: Defaulting unknown proto values to `LEGACY` is compatibility-friendly but may hide bad input. `valueOf` in `fromString` still throws for nonblank invalid strings.

Test signals: Proto round trips, legacy path normalization under both filesystem-path settings, old-client rejection for FSO/OBS, and blank string fallback.
