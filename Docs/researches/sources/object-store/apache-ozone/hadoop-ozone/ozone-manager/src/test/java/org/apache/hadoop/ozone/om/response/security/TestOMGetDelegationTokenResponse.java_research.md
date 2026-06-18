# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/security/TestOMGetDelegationTokenResponse.java

Purpose: Tests `OMGetDelegationTokenResponse` persistence of token renew time.

Important APIs/types/functions: Uses `OzoneTokenIdentifier`, `OMGetDelegationTokenRequest`, `GetDelegationTokenRequestProto`, `UpdateGetDelegationTokenRequest`, `OMGetDelegationTokenResponse`, and `delegationTokenTable`.

Control flow: `setupGetDelegationToken` builds a token identifier for user/renewer/real user `tester`, sets cert serial ID, creates a GetDelegationToken OM request, and extracts the update request produced by `OMGetDelegationTokenRequest`. The test builds an OK OM response, constructs a token response with renew time 1000, adds to batch, commits, then verifies one table row and exact renew time.

State/persistence: Writes `OzoneTokenIdentifier -> renewTime` into `delegationTokenTable`.

Dependencies/integration: Integrates request-side conversion of get-delegation-token request with response-side DB persistence.

Risks/test signals: Only successful token issuance is covered. It does not test renew/cancel responses, token serialization edge cases, or error no-op handling.
