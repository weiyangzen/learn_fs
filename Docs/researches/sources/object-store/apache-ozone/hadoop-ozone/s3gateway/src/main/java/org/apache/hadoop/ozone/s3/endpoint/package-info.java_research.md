<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java

## Purpose
Package-level documentation and JAXB namespace configuration for S3 gateway endpoint DTOs.

## Important APIs, types, and functions
- Declares `@XmlSchema` with namespace `S3Consts.S3_XML_NAMESPACE`.
- Sets `elementFormDefault` to qualified.
- Defines an empty prefix for the S3 XML namespace.

## Control flow
JAXB uses this metadata during marshalling and unmarshalling of endpoint package classes.

## State and persistence behavior
No runtime state or persistence. It controls XML wire format.

## Dependencies and integration points
Applies to response/request classes in `org.apache.hadoop.ozone.s3.endpoint`, including ACL, tagging, listing, and multipart DTOs.

## Risks and edge cases
Changing this namespace would alter client-visible XML and could break AWS SDK compatibility. It must stay aligned with `XmlNamespaceFilter` and `S3Consts`.

## Test signals
XML serialization tests should assert the S3 namespace appears correctly and that unqualified XML request bodies can still be accepted through the namespace filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->
