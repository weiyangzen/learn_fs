<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.s3.tagging` package for S3 object tagging response classes.

Important APIs/types/functions: No executable API. The package groups put/delete tagging response variants for key-table and FSO file-table layouts.

Control flow and persistence: None directly. Concrete classes rewrite `OmKeyInfo` in the key or file table after request-side tag mutation.

Dependencies and integration: Integrated by S3 tagging request classes and OM response batching.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize layout-specific DB keys and metadata preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/s3/tagging/package-info.java -->
