<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.s3` package for S3 secret store related support classes.

Important APIs/types/functions: No executable API. The package groups secret store providers, cache providers, and configuration keys.

Control flow and persistence: None directly. Concrete providers connect S3 secret manager code to local or configured stores and caches.

Dependencies and integration: Integrated by OM S3 secret management and tenant/security responses.

Risks and test signals: Documentation-only risk. Concrete tests should cover provider selection, cache configuration, and secret store persistence mode.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/package-info.java -->
