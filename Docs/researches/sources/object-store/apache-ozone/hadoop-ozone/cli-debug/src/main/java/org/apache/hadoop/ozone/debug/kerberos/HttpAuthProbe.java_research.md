# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/kerberos/HttpAuthProbe.java

Purpose: `HttpAuthProbe` prints HTTP authentication settings for Ozone web endpoints.

Important APIs and types: It extends `ConfigProbe` and reads OM, SCM, datanode, Recon, and S3 Gateway HTTP auth config keys.

Control flow: `test()` prints each key and always returns PASS.

State and persistence behavior: It reads `OzoneConfiguration` only.

Dependencies and integration points: It is part of the Kerberos diagnose flow and helps identify whether WebUI/REST endpoints are configured for Kerberos.

Risks: It does not enforce validation and directly references the S3G key string to avoid a cyclic dependency, so key renames could drift.

Test signals: Printed auth type values for all five services and PASS result.
