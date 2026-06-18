# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestAWSV4AuthValidator.java

## Purpose
`TestAWSV4AuthValidator` validates AWS Signature Version 4 request signature checking against known positive and negative vectors.

## Important APIs, Types, and Functions
- `AWSV4AuthValidator.validateRequest(stringToSign, signature, accessKey)` returns a boolean validation result.
- The parameter provider `data()` supplies canonical string-to-sign values, expected signatures, secret access keys, and expected outcomes.

## Control Flow
The parameterized test passes each tuple to `validateRequest` and asserts the boolean result. Two cases are valid signatures and one differs by the final hex character to assert rejection.

## State and Persistence Behavior
No state or persistence is involved. Inputs are immutable strings.

## Dependencies and Integration Points
The validator is used by S3 authentication paths, including `OzoneDelegationTokenSecretManager` when token type is `S3AUTHINFO`. This test keeps a direct unit signal for the HMAC derivation logic.

## Risks and Edge Cases
The vectors cover positive and one invalid-signature case but do not cover malformed credential scope, unsupported algorithms, date parsing errors, or whitespace/canonicalization issues. Those may be covered at higher S3 request layers.

## Test Signals
The file confirms that the low-level AWS V4 validator matches known HMAC outputs and rejects altered signatures.
