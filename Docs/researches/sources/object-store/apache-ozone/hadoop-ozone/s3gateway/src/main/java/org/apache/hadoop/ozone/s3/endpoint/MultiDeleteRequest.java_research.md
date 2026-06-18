# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/MultiDeleteRequest.java

Purpose: `MultiDeleteRequest` is the JAXB request model for S3 multi-object delete.

Important APIs and flow: root `Delete` contains optional `Quiet` and a list of `Object` elements. Each `DeleteObject` has `Key` and optional `VersionId`. `BucketEndpoint.multiDelete` consumes the object list and quiet flag.

State, dependencies, risks, and tests: state is request body data. Version IDs are parsed but current delete flow ignores versioning. Risks include null object list/key entries, duplicate keys, quiet Boolean nullability versus primitive setter, and unsupported version semantics. Tests should cover quiet true/false, namespace/no-namespace XML, empty objects, null keys, and version ID handling expectations.
