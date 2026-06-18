# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/audit/package-info.java

Purpose: this package descriptor documents the S3 Gateway audit package and identifies `S3GAction` as the gateway's `AuditAction` implementation.

Important APIs and flow: there is no executable code. The documented package is consumed by endpoint and handler classes that write S3G audit records.

State, dependencies, risks, and tests: no state is held. The dependency is documentation alignment with the audit framework. Risk is stale package documentation if more audit types are introduced. Test signal is indirect through S3G audit logging paths.
