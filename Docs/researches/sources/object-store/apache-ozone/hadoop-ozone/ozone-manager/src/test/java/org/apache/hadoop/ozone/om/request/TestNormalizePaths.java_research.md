# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/TestNormalizePaths.java

Purpose: unit tests `OMClientRequest.validateAndNormalizeKey` for normalized filesystem-style keys and raw object-store-style keys.

Important APIs/types: static `validateAndNormalizeKey(boolean, String)`, `OMException`, JUnit assertions, and AssertJ message checks.

Control flow: `testNormalizePathsEnabled` passes normalization enabled and checks leading slash removal, duplicate slash collapsing, `.` removal, `..` parent traversal within bounds, trailing slash handling, preservation of literal multi-dot path segments, and normal relative paths. `testNormalizeKeyInvalidPaths` centralizes invalid cases through `checkInvalidPath`, expecting `OMException` messages containing `Invalid KeyPath`. `testNormalizePathsDisable` passes normalization disabled and verifies raw strings, including repeated slashes and parent segments, are preserved.

State and persistence behavior: none. Behavior is pure string validation/normalization with exception signaling.

Dependencies and integration points: protects OM request key-path interpretation before metadata operations. It is especially relevant for FSO-style path handling and object-store mode compatibility where raw keys are legal.

Risks: expected strings encode exact normalization semantics. Invalid cases are representative but not exhaustive for all special characters or Unicode. Disabled normalization permits forms that enabled mode rejects, so callers must pass the correct flag.

Test signals: verifies valid canonicalization, invalid traversal/empty/root/colon cases, error message content, and no-op behavior when normalization is disabled.
