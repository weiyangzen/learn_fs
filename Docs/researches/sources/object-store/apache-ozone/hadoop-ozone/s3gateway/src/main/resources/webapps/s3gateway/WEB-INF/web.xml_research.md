
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/resources/webapps/s3gateway/WEB-INF/web.xml

Purpose: deployment descriptor for the main S3 gateway web application.

Important APIs and control flow: maps Jersey `ServletContainer` named `jaxrs` to `/*`, configured with `org.apache.hadoop.ozone.s3.GatewayApplication`, and loads it on startup. Registers `EmptyContentTypeFilter` for all requests and the Weld listener.

State, dependencies, integration: no persistent state. Integrates servlet filtering, Jersey resource routing, and CDI bootstrapping. The `optional-content-type` filter removes empty `Content-Type` header values before JAX-RS processing.

Risks and test signals: because the servlet maps `/*`, filters and resource path handling must be correct for all S3 operations. XML formatting includes a line break inside `filter-class` text, which the container must trim/parse as expected. `TestEmptyContentTypeFilter` covers the filter wrapper behavior but not descriptor loading.
