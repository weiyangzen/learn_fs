# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MessageUnmarshaller.java

Purpose: `MessageUnmarshaller<T>` is a generic secure XML body reader for S3 request models, tolerant of XML with or without the S3 namespace.

Important APIs and flow: construction creates a JAXB context for the target class and a secure SAX parser factory via `XMLUtils`. `isReadable` matches the exact target type. `readFrom` creates an XML reader, a JAXB unmarshaller handler, wraps it in `XmlNamespaceFilter` for the S3 namespace, parses the input, and casts the result. Parse failures are converted to S3 `InvalidRequest`. A convenience `readFrom(InputStream)` supports programmatic use.

State, dependencies, risks, and tests: state is the JAXB context, parser factory, and target class. It integrates with multi-delete, ACL, and complete-MPU unmarshallers. Risks include exact type matching missing subclass/generic cases, parser error messages leaking details, and no schema validation beyond JAXB. Tests should cover namespaced and non-namespaced XML, XXE-safe parser behavior, malformed XML, and programmatic reads.
