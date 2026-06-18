<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java

## Purpose
Model and parser for the SigV4 credential scope value.

## Important APIs, types, and functions
- Constructor stores raw credential string and calls `parseCredential`.
- `parseCredential` supports normal five-part credentials and six-part Kerberos-principal access IDs containing `/`.
- Getters expose access key ID, date, AWS region, service, request suffix, and raw credential.
- `createScope` returns `<date>/<region>/<service>/<request>`.

## Control flow
The credential is split on `/`. Five segments map directly. Six segments join the first two as the access key ID to support Kerberos principals. Any other count throws `MalformedResourceException`.

## State and persistence behavior
Only parsed credential fields are stored in memory. No persistence.

## Dependencies and integration points
Used by V4 header and query parsers and later by `StringToSignProducer` via `SignatureInfo.credentialScope`.

## Risks and edge cases
Only one embedded slash in the access key is supported. More complex principal strings or unescaped slashes in access IDs fail parsing. Validation of non-empty fields and date format is left to parser callers.

## Test signals
Tests should cover five-part credentials, Kerberos six-part credentials, malformed segment counts, blank fields, and `createScope` formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java -->
