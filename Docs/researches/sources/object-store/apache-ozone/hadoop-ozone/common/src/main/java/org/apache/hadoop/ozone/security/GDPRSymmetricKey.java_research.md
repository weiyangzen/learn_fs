# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/GDPRSymmetricKey.java

Purpose: Encapsulates a symmetric encryption key and cipher parameters used for GDPR-related Ozone metadata.

Important APIs and types: `newDefaultInstance`, `randomSecret`, constructors from `SecureRandom` or explicit secret/algorithm, `getSecretKey`, `getCipher`, and `acceptKeyDetails`. It stores `SecretKeySpec`, `Cipher`, algorithm, and secret string.

Control flow: The default factory uses a thread-local `SecureRandom` to generate a random alphanumeric secret of the configured default length, then constructs a key with the default GDPR algorithm. Explicit construction validates non-null secret/algorithm and currently requires a 16-character secret before creating `SecretKeySpec` and `Cipher`.

State and persistence behavior: Holds secret material in memory as a `String`, a key spec, and a cipher object. `acceptKeyDetails` exposes the secret and algorithm to a consumer, typically for attaching metadata or persisting key details elsewhere.

Dependencies and integration points: Uses `OzoneConsts` for GDPR constants/charset, Java crypto APIs, Guava preconditions, and Apache Commons random string generation.

Risks: Secret length is hard-coded to 16 characters, so algorithm customization is constrained. Secrets are retained as immutable strings and can be emitted via `acceptKeyDetails`; callers must protect metadata/logging. `Cipher` instances are stateful and not generally thread-safe, so key instances should not be shared for concurrent cipher operations without care.

Test signals: Validate default generation length/algorithm, rejection of null or wrong-length secrets, deterministic construction with explicit secret, `acceptKeyDetails` keys, and cipher/key algorithm compatibility.
