<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java

## Purpose
JAXB DTO for S3 object tagging XML and small validation/conversion helper.

## Important APIs, types, and functions
- Root `S3Tagging` contains `TagSet`.
- `TagSet` contains a list of `Tag`.
- `Tag` contains `Key` and `Value`.
- `fromMap` creates sorted tag XML from an Ozone tag map.
- `validate` requires a non-null tag set, at least one tag, and non-null key/value fields.

## Control flow
PUT tagging unmarshalling fills this DTO, then `validate` performs structural checks before endpoint-level tag policy validation. GET tagging uses `fromMap`, sorting entries by key for stable AWS-compatible output.

## State and persistence behavior
No persistence occurs here. It represents tag state exchanged with clients.

## Dependencies and integration points
Used by `ObjectTaggingHandler` and JAXB marshalling with `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
This class does not enforce S3 tag count, character, prefix, or length limits; those are enforced elsewhere. Empty tag sets are rejected, so callers cannot use PUT tagging to clear tags.

## Test signals
Tests should cover XML unmarshalling, missing `TagSet`, empty tags, missing key/value, stable sorted output, and coordination with endpoint tag validators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java -->
