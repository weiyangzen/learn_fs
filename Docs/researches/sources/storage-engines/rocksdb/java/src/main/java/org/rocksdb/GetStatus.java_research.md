# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/GetStatus.java

Purpose: result object for fetch-into-buffer operations where the destination may be too small. It carries a `Status` and `requiredSize`.

Control flow is package-private construction plus `fromStatusCode(Status.Code, int)`, which creates a `Status` with subcode zero and null state. Fields are public final, making the object immutable. State is copied Java result data, not native-owned. Dependencies include `Status.Code` and `Status.SubCode`.

Risks: `requiredSize` can be larger than the supplied buffer and must be checked by callers; `fromStatusCode` discards richer status state/subcode. Tests should cover success, not-found/error statuses, too-small buffer size reporting, and callers that retry with the required size.
