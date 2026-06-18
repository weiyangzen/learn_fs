# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/CommonHeadersContainerResponseFilter.java

Purpose: this response filter adds S3-compatible common response headers to every gateway response.

Important APIs and flow: it injects request-scoped `RequestIdentifier` and appends `Server: Ozone`, `x-amz-id-2`, and `x-amz-request-id` to `ContainerResponseContext` headers. It does not inspect status or entity type, so success and error responses receive the same common identifiers.

State, dependencies, risks, and tests: state comes from `RequestIdentifier`, which is generated per request; there is no persistence. The filter integrates with all Jersey resources and exception mappers. Risks are duplicate headers if another layer adds the same names and missing identifiers if CDI injection fails. Test signals include response-header assertions in S3 endpoint and error-mapper tests.
