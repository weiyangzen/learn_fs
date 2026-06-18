
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/TestVirtualHostStyleFilter.java

Purpose: tests conversion of virtual-host-style S3 requests to path-style URIs.

Important APIs and control flow: setup configures HTTP address `localhost:9878` and S3 domain `localhost`. `createContainerRequest` builds Jersey `ContainerRequest` objects with base URI, request URI, method, host header, and mocked security/properties. Tests verify `mybucket.localhost:9878` plus optional path/query becomes `/mybucket[/key]?query`, while path-style host remains unchanged. Parameterized invalid host tests assert `InvalidRequestException` for domain mismatch or invalid host format.

State, dependencies, integration: uses `OzoneConfiguration`, Jersey container request classes, and mocked security context. Integrated with the gateway request filter chain before endpoint matching.

Risks and test signals: configured domain parsing strips port from the HTTP address. Tests validate URI rewriting and query preservation but not HTTPS, IPv6, or multi-label domain edge cases.
