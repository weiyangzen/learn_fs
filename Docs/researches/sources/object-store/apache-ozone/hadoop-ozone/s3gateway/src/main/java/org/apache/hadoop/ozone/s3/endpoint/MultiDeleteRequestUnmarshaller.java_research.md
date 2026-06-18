# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequestUnmarshaller.java

Purpose: `MultiDeleteRequestUnmarshaller` registers the generic XML unmarshaller for `MultiDeleteRequest` bodies.

Important APIs and flow: it is a singleton JAX-RS provider producing `application/xml`, and its constructor binds `MessageUnmarshaller` to `MultiDeleteRequest.class`. All read behavior is inherited.

State, dependencies, risks, and tests: inherited state is JAXB context and parser factory. It integrates with `BucketEndpoint.multiDelete` body binding. Risks are inherited from `MessageUnmarshaller`, especially malformed XML and namespace tolerance. Tests should assert Jersey selects this reader and parses delete XML with and without namespace.
