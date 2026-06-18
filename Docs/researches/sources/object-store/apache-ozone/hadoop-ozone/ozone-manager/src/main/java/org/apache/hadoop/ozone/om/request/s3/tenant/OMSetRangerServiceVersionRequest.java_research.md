
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/s3/tenant/OMSetRangerServiceVersionRequest.java

Purpose: Internal OM request used by `OMRangerBGSyncService` to persist the Ranger Ozone service version observed during background policy synchronization.

Important APIs and types: Extends `OMClientRequest`; uses `SetRangerServiceVersionRequest`, `SetRangerServiceVersionResponse`, `OzoneConsts.RANGER_OZONE_SERVICE_VERSION_KEY`, `metaTable`, and `OMSetRangerServiceVersionResponse`.

Control flow: `validateAndUpdateCache` builds a normal OK response, reads the proposed Ranger service version, stores it as a string in the metadata table cache at the transaction index, attaches an empty proto response, and returns a response object carrying the meta key/value for double-buffer commit.

State and persistence behavior: Mutates only the OM metadata table entry for the Ranger service version. It does not perform locking, metrics, ACL checks, or auditing because it is an internal sync request.

Dependencies and integration points: Couples the Ranger background sync service to OM DB replication so followers learn the last synchronized service version.

Risks: The handler trusts the caller and accepts any long value. Tests should verify meta-table cache update, response contents, and replay/idempotence for repeated version values.
