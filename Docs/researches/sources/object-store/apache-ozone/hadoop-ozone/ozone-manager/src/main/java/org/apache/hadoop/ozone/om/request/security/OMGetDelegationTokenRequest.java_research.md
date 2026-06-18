
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/security/OMGetDelegationTokenRequest.java

Purpose: Converts a client get-delegation-token request into a replicated update request containing the leader-generated token and renew interval.

Important APIs and types: Extends `OMClientRequest`; uses `GetDelegationTokenRequestProto`, `UpdateGetDelegationTokenRequest`, `OMPBHelper`, `OzoneTokenIdentifier`, `delegationTokenTable`, and `OMGetDelegationTokenResponse`.

Control flow: `preExecute` asks `OzoneManager.getDelegationToken` for a token, wraps it in `UpdateGetDelegationTokenRequest`, preserves command type/client ID/trace ID, and audits generation failures. Validation handles null-token responses when security is disabled, decodes the generated token, adds renewer audit data, updates the in-memory token manager to compute renew time, writes the renew time to the delegation token table cache, and returns the original token response.

State and persistence behavior: Adds/updates token state in memory and persists token renew time keyed by `OzoneTokenIdentifier` in the delegation token table cache.

Dependencies and integration points: Coordinates security manager token generation, Ratis replication of generated secrets, OM DB cache, audit logging, protocol version compatibility, and security-disabled behavior.

Risks: Token generation happens only on the leader before Ratis replication, so all followers depend on the update request payload. Tests should cover security disabled, token renewer audit field, trace ID preservation, cache update, and invalid token proto.
