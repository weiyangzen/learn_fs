
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/EndpointBuilder.java

Purpose: reusable builder for constructing S3 endpoint instances in unit tests without a full Jersey/CDI container.

Important APIs and control flow: stores optional base endpoint, client, config, headers, request context, request ID, and signature info. Constructor prepares default `OzoneConfiguration`, `RequestIdentifier`, mocked `SignatureInfo` with signed payload, and mocked request/URI query/path maps. `build` creates or reuses the endpoint, injects client/config/context/headers/request ID/signature info, calls `initialization`, and returns the ready endpoint. Static factories create builders for root, bucket, bucket ACL handler, and object endpoints.

State, dependencies, integration: per-builder mutable test setup state. Integrates endpoint tests with `OzoneClientStub`, mocked JAX-RS APIs, and endpoint lifecycle methods.

Risks and test signals: because it bypasses Jersey/CDI, tests using it do not validate production injection, filters, or servlet mappings. Defaults such as signed payload may hide unsigned-request paths unless tests override them.
