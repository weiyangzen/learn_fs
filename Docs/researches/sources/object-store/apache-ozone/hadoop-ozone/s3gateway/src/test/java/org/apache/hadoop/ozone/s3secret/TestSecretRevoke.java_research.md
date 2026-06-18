# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3secret/TestSecretRevoke.java

## Purpose
Unit tests for the S3 secret revocation REST endpoint. It verifies principal-derived and explicit-user revocation plus endpoint status mapping for repeated or failed revokes.

## Important APIs, types, and functions
The test drives `S3SecretManagementEndpoint.revoke()` and `revoke(String)`. It mocks `ObjectStoreStub.revokeS3Secret`, JAX-RS request context objects, and uses `OMException.ResultCodes.S3_SECRET_NOT_FOUND` and `ACCESS_DENIED`.

## Control flow
`setUp` injects a stub Ozone client wrapping a mocked object store and an empty request URI context. Self-service tests mock the security principal, call `revoke`, and verify the object store is called with the principal name. Explicit revoke bypasses the security context. Sequential revoke first succeeds, then makes the object store throw `S3_SECRET_NOT_FOUND`; generic OM failure uses `ACCESS_DENIED`.

## State and persistence behavior
No persistent state is mutated. The only state transition is simulated by changing the mock from success to throwing after the first call.

## Dependencies and integration points
The test guards endpoint integration with `ObjectStore.revokeS3Secret`, security principal lookup, and REST status conversion.

## Risks and edge cases
Only selected OM exceptions are covered. Authorization semantics and real OM secret table persistence are not exercised.

## Test signals
Signals include Mockito call counts/arguments and HTTP statuses: `OK` on success, `NOT_FOUND` for missing secret, and `INTERNAL_SERVER_ERROR` for access-denied-style failures.
