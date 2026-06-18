
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretEnabledEndpointRequestFilter.java

Purpose: rejects S3 secret endpoint requests unless `ozone.s3g.secret.http.enabled` is true.

Important APIs and control flow: injected `OzoneConfiguration` is queried with default `false`. If disabled, the request is aborted with HTTP 400 and entity `S3 Secret endpoint is disabled.`; otherwise the request proceeds.

State, dependencies, integration: holds injected config and is registered as a Jersey provider through `@Provider` plus the `@S3SecretEnabled` name binding. Integrated with `S3SecretManagementEndpoint`.

Risks and test signals: returns bad request rather than forbidden/not found, making disabled endpoint behavior visible. If injection fails, the filter will NPE. No direct listed unit test covers this filter.
