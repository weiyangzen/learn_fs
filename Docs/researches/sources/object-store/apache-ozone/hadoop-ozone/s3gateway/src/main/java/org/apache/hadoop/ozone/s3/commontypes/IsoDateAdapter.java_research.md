# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/commontypes/IsoDateAdapter.java

Purpose: `IsoDateAdapter` marshals Java `Instant` values into S3 XML timestamp strings.

Important APIs and flow: construction builds a UTC `DateTimeFormatter` with pattern `yyyy-MM-dd'T'HH:mm:ss.SSSX`. `marshal` formats the `Instant`; `unmarshal` is unsupported because these DTOs are response-only for date fields.

State, dependencies, risks, and tests: state is the formatter instance. It integrates with bucket/key/multipart response DTOs. Risks include null `Instant` causing formatter failure, AWS compatibility around millisecond precision, and unsupported unmarshal if reused for request parsing. Tests should marshal known instants and assert UTC output.
