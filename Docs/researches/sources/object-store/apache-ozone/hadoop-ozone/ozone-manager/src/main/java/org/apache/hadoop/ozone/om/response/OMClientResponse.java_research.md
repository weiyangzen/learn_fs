# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/OMClientResponse.java

Purpose: `OMClientResponse` is the abstract base for OM response-side persistence. It wraps the protobuf `OMResponse`, carries lock details, and defines the DB batch update contract.

Important APIs and types: `checkAndUpdateDB` calls `addToDBBatch` only when status is `OK`. `checkStatusNotOK` guards error constructors. `getBucketLayout` defaults to `BucketLayout.DEFAULT`. `setOmLockDetails` records lock acquisition/release metadata.

Control flow: Request classes produce concrete responses after cache mutation. Later OM transaction application calls `checkAndUpdateDB`, which gates persistence on success unless subclasses override for partial-success statuses.

State and persistence behavior: The base stores immutable `OMResponse` and mutable `OMLockDetails`. Actual persistence is delegated to subclasses using `BatchOperation`.

Dependencies and integration points: It links request handling, Ratis transaction replay/apply, OM metadata manager tables, bucket layout selection, and lock observability.

Risks and test signals: Subclasses with partial success must override `checkAndUpdateDB`. Tests should verify error constructors call `checkStatusNotOK`, OK responses write exactly once, and bucket-layout overrides route to correct tables.
