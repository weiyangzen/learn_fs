<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java

Purpose: Declares the `org.apache.hadoop.ozone.om.response.security` package for general OM security request responses.

Important APIs/types/functions: No executable API. The package groups delegation-token get, renew, and cancel response classes.

Control flow and persistence: None directly. Concrete responses mutate `DELEGATION_TOKEN_TABLE`.

Dependencies and integration: Integrated by OM security request handling and delegation token management.

Risks and test signals: Documentation-only risk. Concrete tests should emphasize status-gated token table writes and null token handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/security/package-info.java -->
