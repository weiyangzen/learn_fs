# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/S3GatewayWebAdminServer.java

Purpose: `S3GatewayWebAdminServer` serves static/admin content and protects the `/secret/*` endpoint when the S3 secret HTTP feature is enabled.

Important APIs and flow: construction calls the base server, adds a favicon redirect servlet, and invokes `addSecretAuthentication`. If secret HTTP is enabled, the method requires Hadoop security and Kerberos auth type, builds Kerberos principal/keytab params, creates an `AuthenticationFilter`, and maps it to `/secret/*`; otherwise it throws an `IllegalStateException`. The server maps web-admin address, auth, bind-host, keytab, and SPNEGO config keys to S3G constants.

State, dependencies, risks, and tests: server state is Jetty/BaseHttpServer state plus optional filter mappings. It depends on Hadoop auth, UGI security state, servlet handlers, and S3 secret config keys. Risks include exposing secrets if auth is disabled incorrectly, hard failure on non-Kerberos secret auth, and principal hostname substitution using the configured bind host. Tests should cover disabled secret endpoint, secured Kerberos filter installation, and favicon redirect.
