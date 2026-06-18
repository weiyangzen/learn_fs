<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java

## Purpose
SAX filter that forces all element callbacks into a configured namespace, allowing namespace-insensitive client XML to be read as S3 namespace-qualified XML.

## Important APIs, types, and functions
- Constructor accepts namespace URI.
- `startElement` and `endElement` replace the incoming URI with the configured namespace before delegating.

## Control flow
During SAX parsing, each element start/end event is rewritten with the target namespace while local name, qualified name, and attributes pass through.

## State and persistence behavior
Stores only the configured namespace string. It performs no persistence.

## Dependencies and integration points
Used by XML unmarshalling infrastructure for endpoint DTOs that expect `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
The filter does not rewrite attribute namespaces. If client XML uses namespace-sensitive attributes, callers must handle those separately.

## Test signals
XML parsing tests should include S3 request bodies with and without explicit default namespaces and verify they unmarshal into the same DTOs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java -->
