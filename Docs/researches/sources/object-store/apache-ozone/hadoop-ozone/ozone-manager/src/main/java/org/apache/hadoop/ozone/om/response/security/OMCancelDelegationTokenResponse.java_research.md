<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java

Purpose: Removes a delegation token from OM metadata after a successful cancel-delegation-token request.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier` and `OMResponse`. `addToDBBatch` obtains `getDelegationTokenTable()` and deletes the token only when response status is `OK`.

Control flow and persistence: A successful cancel batches `deleteWithBatch(batchOperation, ozoneTokenIdentifier)` against `DELEGATION_TOKEN_TABLE`. There is no null guard inside the OK branch, so request construction must provide the identifier on success.

Dependencies and integration: Used by OM security token cancellation request handling. Depends on `OzoneTokenIdentifier` as the table key and OM response status for gating.

Risks and test signals: Null token on OK would produce table-layer failure or undefined behavior. Tests should cover successful deletion, status-not-OK no-op, missing token defensive behavior if supported by table implementation, and replay idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMCancelDelegationTokenResponse.java -->
