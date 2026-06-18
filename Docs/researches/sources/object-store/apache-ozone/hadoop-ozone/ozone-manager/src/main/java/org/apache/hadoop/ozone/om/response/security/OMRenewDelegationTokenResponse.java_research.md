<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java

Purpose: Updates the renewal time for an existing delegation token after a successful renew request.

Important APIs/types/functions: Extends `OMClientResponse`. The constructor stores nullable `OzoneTokenIdentifier`, new renew time, and `OMResponse`. `addToDBBatch` writes the token key and renew time to `DelegationTokenTable` when status is `OK`.

Control flow and persistence: Performs a batched put on `DELEGATION_TOKEN_TABLE`. Unlike get-token response, there is no null guard in the OK branch, so request validation must guarantee the identifier exists on success.

Dependencies and integration: Used by renew-delegation-token request handling and OM token persistence.

Risks and test signals: Null token on success and incorrect renew time are primary risks. Tests should verify update of existing token, failure no-op, replay idempotency, and boundary renewal times.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/OMRenewDelegationTokenResponse.java -->
