# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteResponse.java

Purpose: `MultiDeleteResponse` is the JAXB XML result for S3 multi-object delete.

Important APIs and flow: it stores `Deleted` entries and `Error` entries. `DeletedObject` includes key and version ID; `Error` includes key, code, and message. `BucketEndpoint.multiDelete` appends deleted rows unless quiet mode is true and appends errors for failed keys or all-key internal failures.

State, dependencies, risks, and tests: state is response-only. It integrates with multi-delete endpoint logic and S3 error code mapping. Risks include version ID not being XML-annotated in `DeletedObject`, quiet mode suppressing success rows but not errors, and all-key errors using key `ALL`. Tests should assert mixed success/error XML, quiet behavior, and version field serialization expectations.
