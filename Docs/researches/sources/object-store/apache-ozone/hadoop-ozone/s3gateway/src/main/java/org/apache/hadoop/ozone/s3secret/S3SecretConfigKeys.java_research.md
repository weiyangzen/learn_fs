
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3secret/S3SecretConfigKeys.java

Purpose: constants for S3 secret HTTP endpoint configuration.

Important APIs and control flow: exposes `ozone.s3g.secret.http.enabled` with default `false`, the auth config prefix `ozone.s3g.secret.http.auth.`, auth type key, and default auth type `kerberos`. Private constructor prevents instantiation.

State, dependencies, integration: no runtime state. Used by `S3SecretEnabledEndpointRequestFilter` and likely server configuration code outside this subset.

Risks and test signals: endpoint is disabled by default, which is conservative. A config-key typo changes endpoint exposure behavior. No direct listed test validates these constants.
