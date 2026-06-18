# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestGDPRSymmetricKey.java

Purpose: tests `GDPRSymmetricKey` creation with generated and supplied secrets.

Important APIs/types/functions: exercises constructors `GDPRSymmetricKey(SecureRandom)` and `GDPRSymmetricKey(String, String)`, `getCipher`, and `acceptKeyDetails`.

Control flow and state: default generation uses `SecureRandom` and must create a cipher whose algorithm equals `OzoneConsts.GDPR_ALGORITHM_NAME`. Valid 16-character input also creates the expected cipher and exposes non-empty key details. Invalid 5-character input throws `IllegalArgumentException` with an exact secret-length message.

Dependencies and integration points: uses Java crypto, Commons `RandomStringUtils.secure`, and Ozone GDPR constants. These keys support GDPR metadata encryption/decryption behavior.

Risks and test signals: catches wrong algorithm selection, empty persisted key detail fields, and weak/invalid secret length acceptance. It does not test actual encryption/decryption output.
