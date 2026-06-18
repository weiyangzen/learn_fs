
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMRenewDelegationTokenRequest.java

Purpose: Renews an existing delegation token on the leader and replicates the new expiry time to all OMs.

Important APIs and types: Extends `OMClientRequest`; uses `RenewDelegationTokenRequestProto`, `UpdateRenewDelegationTokenRequest`, `RenewDelegationTokenResponseProto`, `OzoneTokenIdentifier`, `delegationTokenTable`, and `OMRenewDelegationTokenResponse`.

Control flow: `preExecute` converts the token proto, builds audit metadata, decodes the identifier, calls `ozoneManager.renewDelegationToken`, embeds the original request and new expiry time into an update request, and preserves trace ID. Validation decodes the token, updates the in-memory delegation token manager with the new expiry, writes the expiry to the token table cache, returns the renewed response, and audits success/failure.

State and persistence behavior: Updates memory and DB cache renewal time for the token. No explicit lock is taken; ordering comes from OM state machine transaction sequencing.

Dependencies and integration points: Integrates Hadoop token protocol conversion, OM delegation token manager, audit logging, Ratis update conversion, and response persistence.

Risks: Renewal authorization is leader-only in `preExecute`; followers trust the embedded expiry. Tests should cover expired/unauthorized tokens, renewer audit map, table cache update, trace preservation, and interrupted/malformed token paths.
