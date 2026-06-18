<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.multipart` package and documents that it contains S3 multipart upload response classes.

Important APIs/types/functions: No executable API is defined. The package groups response classes for initiating, committing, aborting, completing, and expiring multipart uploads, including object-store and FSO layout variants.

Control flow and persistence: None directly. Persistence behavior lives in the response classes in this package, which mutate open-key/open-file, multipart-info, key/file, deleted, directory, and bucket tables through OM batch operations.

Dependencies and integration: The package belongs to OM response handling and is consumed by S3 multipart request implementations and double-buffer replay.

Risks and test signals: Package metadata risk is limited to stale documentation. Tests should focus on the concrete response classes and on package-level cleanup table coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/multipart/package-info.java -->
