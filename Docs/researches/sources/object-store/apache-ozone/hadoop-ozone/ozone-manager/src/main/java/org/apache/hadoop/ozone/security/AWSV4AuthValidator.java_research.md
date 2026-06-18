<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java

Purpose: Package-private utility for AWS Signature Version 4 validation used by Ozone S3 authentication.

Important APIs/types/functions: `hash(String)` returns a SHA-256 hex digest. `validateRequest(String strToSign, String signature, String userKey)` derives the AWS V4 signing key and compares the expected HMAC hex string. `getSigningKey` parses date, region, and service from the credential-scope line of the string-to-sign. `sign` uses a per-thread cached `Mac` for `HmacSHA256`.

Control flow: Validation splits `strToSign`, derives `kDate`, `kRegion`, `kService`, and final `aws4_request` key using chained HMAC operations, signs the full string-to-sign, hex-encodes it, and compares it to the request signature.

State and persistence behavior: No persistence. State is a `ThreadLocal<Mac>` cache to reduce allocation while keeping `Mac` instances thread-confined.

Dependencies and integration points: Used by `OzoneDelegationTokenSecretManager.validateS3AuthInfo`; reachable from `S3SecurityUtil` through delegation-token password retrieval. Depends on Kerby `Hex`, Hadoop `StringUtils`, JCA `MessageDigest`, and `Mac`.

Risks: The string-to-sign parsing assumes AWS V4 layout and does no length validation before indexing. Signature comparison uses ordinary string equality rather than constant-time comparison. Debug logging of signing key material is guarded by debug level but still sensitive if enabled.

Test signals: Tests should include valid AWS V4 signatures, malformed string-to-sign values, wrong secret/region/service/date cases, concurrent validation to exercise the thread-local `Mac`, and hash formatting with leading zeros.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/security/AWSV4AuthValidator.java -->
