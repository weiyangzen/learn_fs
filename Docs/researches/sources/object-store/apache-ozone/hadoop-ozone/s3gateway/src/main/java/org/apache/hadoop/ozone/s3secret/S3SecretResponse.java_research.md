
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretResponse.java

Purpose: JAXB response DTO for generated S3 credentials.

Important APIs and control flow: annotated as XML root `S3Secret` with field access. Contains `awsAccessKey` and `awsSecret` elements with standard getters and setters.

State, dependencies, integration: mutable data holder populated by `S3SecretManagementEndpoint.generateInternal` from `S3SecretValue` and serialized by JAX-RS/JAXB. No persistence.

Risks and test signals: it serializes secret material directly, so endpoint filtering and transport security are critical. No direct listed serialization test for this DTO.
