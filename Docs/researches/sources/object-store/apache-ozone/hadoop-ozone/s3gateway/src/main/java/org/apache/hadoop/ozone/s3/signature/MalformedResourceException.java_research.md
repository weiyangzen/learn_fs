<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java

## Purpose
Checked exception used by signature parsers to report malformed auth resources while preserving the offending header/query value.

## Important APIs, types, and functions
- Stores immutable `resource`.
- Constructors accept resource only or message plus resource.
- `getResource` exposes the value used for S3 error resource and audit logging.

## Control flow
Parsers throw this exception when they recognize their auth style but validation fails. `AWSSignatureProcessor` catches it, audits, and maps it to `AuthorizationHeaderMalformed`.

## State and persistence behavior
In-memory exception state only. No persistence.

## Dependencies and integration points
Used by all signature parsers and `Credential`.

## Risks and edge cases
Some parser paths pass user-supplied full authorization headers as resource; callers should avoid logging sensitive signatures at inappropriate levels.

## Test signals
Tests should assert processor mapping and audit resource selection for malformed auth inputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java -->
