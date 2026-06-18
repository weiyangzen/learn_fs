# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_IntegrityCheck.cpp

Purpose: Tests CryFS CLI integrity protections around filesystem ID, filesystem key, rollback of basedir contents, and rollback while mounted.

Important APIs and types: Uses `CliTest`, `CryConfigFile`, `ErrorCodes`, `Scrypt`, `DataFixture`, `TempDir`, `CachingFsBlobStore`, and a `FakeCryKeyProvider`. Helper methods modify config fields, write/read files, recursively copy basedirs, and verify reads.

Control flow: Tests create or mount a test filesystem, tamper with config or basedir state, run CLI mount/integrity paths, and assert expected failures or unmount behavior when rollback is detected.

State and persistence behavior: Uses real temporary basedir/mountdir/config state and blobstore contents. The rollback tests intentionally copy and restore filesystem directory snapshots.

Dependencies and integration points: Integrates CLI setup, config encryption/KDF, blobstore caching, filesystem IDs/keys, and error-code handling.

Risks: These tests are filesystem- and mount-sensitive. Tampering helpers must modify the intended metadata without corrupting unrelated setup.

Test signals: Mount fails for incorrect filesystem ID/key, basedir rollback is rejected, and rollback while mounted causes unmount/error behavior.
