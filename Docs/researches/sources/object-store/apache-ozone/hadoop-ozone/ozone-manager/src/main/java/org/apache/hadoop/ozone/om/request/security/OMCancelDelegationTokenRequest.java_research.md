
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMCancelDelegationTokenRequest.java

Purpose: Cancels an Ozone delegation token through leader-side authorization and replicated OM DB/cache removal.

Important APIs and types: Extends `OMClientRequest`; uses `CancelDelegationTokenRequestProto`, `Token<OzoneTokenIdentifier>`, `OMPBHelper`, `delegationTokenTable`, `OMCancelDelegationTokenResponse`, and `buildTokenAuditMap`.

Control flow: `preExecute` populates user info, converts the proto token, audits failures, and calls `ozoneManager.cancelDelegationToken` to perform authorization without removing persisted state. `validateAndUpdateCache` decodes the token identifier, removes it from the in-memory delegation token manager, writes a tombstone cache entry to the delegation token table, builds a cancel response, and audits.

State and persistence behavior: Removes token state from memory and schedules deletion from the token table via cache tombstone at the transaction index.

Dependencies and integration points: Integrates Hadoop token serialization, OM delegation token manager, OM metadata table persistence, audit logging, and response flushing.

Risks: Logger is initialized with `OMGetDelegationTokenRequest.class`, which affects log categorization. Tests should cover unauthorized cancel in `preExecute`, successful table tombstone, malformed token decoding, and audit contents.
