# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/RequestIdentifier.java

Purpose: `RequestIdentifier` creates AWS-style request identifiers for response headers and audit parameters.

Important APIs and flow: construction generates an 8-to-15 character alphanumeric `amzId` using `SecureRandom` through `RandomStringUtils`, and an Ozone request ID via `OzoneUtils.getRequestID()`. Getters expose both values.

State, dependencies, risks, and tests: state is immutable per request due to `@RequestScoped`; no persistence exists. It integrates with `CommonHeadersContainerResponseFilter` and `EndpointBase.auditMessageFor`. Risks are identifier collision probability, expensive secure randomness under heavy load, and CDI scope mistakes producing reused identifiers. Tests should assert per-instance non-null IDs and response header propagation.
