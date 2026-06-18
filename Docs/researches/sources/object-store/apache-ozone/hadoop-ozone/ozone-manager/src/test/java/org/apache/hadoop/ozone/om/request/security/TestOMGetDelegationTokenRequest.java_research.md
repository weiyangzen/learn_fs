# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/security/TestOMGetDelegationTokenRequest.java

## Purpose
This JUnit 5 test class validates `OMGetDelegationTokenRequest`, the Ozone Manager request path that obtains and persists delegation-token renewal metadata. It extends `TestOMDelegationTokenRequest`, inheriting a mocked `OzoneManager`, `OMMetadataManager`, and configuration-backed metadata store. The tests focus on the two-phase OM request lifecycle: `preExecute` asks `OzoneManager` for a token and rewrites the request into an update request, while `validateAndUpdateCache` persists the token renew time into the delegation token table.

## Important APIs and Types
Key collaborators are `OzoneDelegationTokenSecretManager`, `OzoneTokenIdentifier`, Hadoop `Token<OzoneTokenIdentifier>`, `GetDelegationTokenRequestProto`, `OMRequest`, `OMClientResponse`, and OM response `Status`. `setupToken()` creates a concrete token using `OzoneTokenIdentifier` bytes, random password bytes, `KIND_NAME`, and an OM service address. `setValidateAndUpdateCache()` centralizes the real flow: call `preExecute`, wrap the modified request in a new `OMGetDelegationTokenRequest`, then call `validateAndUpdateCache`.

## Control Flow and State
`setupGetDelegationToken()` wires mocks for token manager, audit logger, and layout version manager. `testPreExecuteWithNonNullToken` stubs `ozoneManager.getDelegationToken(tester)` and `getTokenRenewInterval()`, then verifies the original command/client id are preserved while `UpdateGetDelegationTokenRequest` gains a renew interval and token response. `testPreExecuteWithNullToken` verifies the response is absent when OM returns no token. The validate tests assert that a non-null token causes `secretManager.updateToken(...)` to return a renew time that is cached in `omMetadataManager.getDelegationTokenTable()` under the decoded identifier. Null-token validation remains `OK` but leaves no table entry. A malformed empty `Token` exercises decode failure, where the request response contains a token response but final status is not `OK`.

## Dependencies and Integration Points
The tests depend on protobuf request/response builders, OM audit infrastructure, layout-version manager defaults, and the delegation-token secret manager contract. The integration point under test is the transition from pre-executed token material to durable OM metadata.

## Risks and Test Signals
The class catches regressions where `preExecute` mutates unrelated request fields, omits renewal intervals, fails to serialize token responses, or writes invalid delegation-token table entries. The malformed-token path is important because deserialization errors must convert into failed OM responses without corrupting token state.
