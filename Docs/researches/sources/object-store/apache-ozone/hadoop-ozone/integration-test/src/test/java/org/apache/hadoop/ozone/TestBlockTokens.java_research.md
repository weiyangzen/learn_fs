# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestBlockTokens.java

Purpose: secure HA integration tests for block token validation against SCM secret key rotation, expiry, unknown key IDs, and invalid token passwords.

Important APIs/types/functions: `init`, `createTestData`, `blockTokensHappyCase`, `blockTokenFailsOnExpiredSecretKey`, `blockTokenOnExpiredSecretKeyRetrySuccessful`, `blockTokenFailsOnWrongSecretKeyId`, `blockTokenFailsOnWrongPassword`, `extractSecretKeyId`, `getTestKeyInfo`, `readData`, secure setup helpers, and `startCluster`. It uses MiniKdc, `MiniOzoneHAClusterImpl`, `SecretKeyManager`, `ManagedSecretKey`, `OzoneBlockTokenIdentifier`, `KeyInputStream`, `BlockInputStreamFactoryImpl`, and Ozone client/OM key metadata.

Control flow: setup disables system exits, starts MiniKdc, writes Kerberos principals/keytabs for SCM/OM/DN/SPNEGO/test user, configures secret-key rotate/check/expiry durations, enables block/container tokens, starts a 3-SCM/1-OM secure HA cluster, creates one test key, and retains a client. The happy case confirms key metadata token uses the current SCM key, reads from DNs, waits for key rotation, then verifies old token still works before expiry. Expiry failure waits until the signing secret key expires and expects `BLOCK_TOKEN_VERIFICATION_FAILED`. Retry success uses `KeyInputStream` retry callback to fetch fresh key info after expiry. Wrong-key and wrong-password tests mutate embedded block tokens in `OmKeyLocationInfo` and assert verification failure messages.

State and persistence: Kerberos keytabs in temp dir, secure Ozone cluster, SCM secret key manager state, OM key metadata tokens, client-side mutated token objects, and stream reads from datanodes. Test disables checksum verification to isolate token behavior.

Dependencies and integration points: Hadoop security/Kerberos, SCM secret key rotation, OM-generated key info, datanode block token verifier, `KeyInputStream` retry path, HA SCM active selection.

Risks: timing depends on short secret-key durations and `waitFor` polling. Mutating token objects in returned key info assumes in-memory metadata objects are isolated enough for the test. Static cluster and KDC lifecycle make failures expensive. Uses same Kerberos principal strings for several services in test mode.

Test signals: exact secret key ID match, successful 100-byte reads, expired-key verification result/message, retry recovery, unknown secret-key message, and invalid password message.
