<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java

Purpose: Persists a newly issued delegation token and its renewal time.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier`, `renewTime`, and `OMResponse`. `addToDBBatch` writes to `DelegationTokenTable` only when token is non-null and status is `OK`.

Control flow and persistence: Performs `putWithBatch(batchOperation, ozoneTokenIdentifier, renewTime)` under `DELEGATION_TOKEN_TABLE`. The renew time defaults to `-1L` but is expected to be supplied for successful tokens.

Dependencies and integration: Used by get-delegation-token request handling and OM security token manager state.

Risks and test signals: Renewal time correctness controls token validity. Tests should cover successful table insert, null-token no-op, status failure no-op, and persisted value matching request-calculated renewal time.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMGetDelegationTokenResponse.java -->
