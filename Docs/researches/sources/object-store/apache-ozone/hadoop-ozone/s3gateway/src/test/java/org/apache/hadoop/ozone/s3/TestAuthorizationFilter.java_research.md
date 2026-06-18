
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestAuthorizationFilter.java

Purpose: tests AWS authorization filter parsing and string-to-sign generation.

Important APIs and control flow: parameterized failure cases build mocked `ContainerRequestContext` with malformed/stale/empty/unsupported auth headers and verify HTTP 400 or 403 plus expected error messages. Success cases cover path-style and virtual-host style request URIs, configuring `AWSSignatureProcessor` and `SignatureInfo`, invoking `AuthorizationFilter.filter`, then computing the expected canonical request and AWS4 string-to-sign for assertion. `setupContext` mocks headers, query params, path params, method, and URI.

State, dependencies, integration: uses current date/time in AWS date format, mocked JAX-RS context, signature parser/processor classes, and S3 constants. No persistent state.

Risks and test signals: tests use dynamic current date/time, so expected strings track the test run date. They do not verify cryptographic signature validation, only parsing/canonicalization state. They explicitly reject AWS V2 signatures.
