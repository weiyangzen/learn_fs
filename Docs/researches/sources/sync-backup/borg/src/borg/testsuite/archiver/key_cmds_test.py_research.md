<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py

Purpose: integration coverage for `borg key` and related repository-key behavior across local, remote, and binary archivers. It exercises passphrase rotation, moving key material between repokey and keyfile storage, key export/import variants, paper keys, KDF metadata, and the multi-key-per-repository workflow.

Important APIs and helpers: `cmd`, `generate_archiver_tests`, `_extract_repository_id`, `_set_repository_id`, `Repository`, `AESOCBKey`, `CHPOKey`, `Passphrase`, `is_keyfile`, `keyfile_parse`, `msgpack`, `KeyBlobStorage`, and test helpers `_expect_error`, `_key_id_for_label`, `_exported_label`, `_store_corrupted_borg_key`. The second half defines `ENC_ARGS_AND_MODE` and `ENC_ARGS` for repokey/keyfile parametrization.

Control flow: tests create repositories with `RK_ENCRYPTION`, `KF_ENCRYPTION`, authenticated mode, or Blake3 modes, then mutate key location or passphrase and verify `repo-info`, key files, repository key blobs, and unlockability. Export/import tests round-trip keyfiles, repokeys, QR HTML, paper-key text, and invalid inputs. Multi-key tests add labels, remove by label/id/current passphrase, verify admin/last-key protection, confirm secrets are shared, and assert key selection ambiguity is rejected.

State and persistence: writes to the repository key store, `archiver.keys_path`, explicit `BORG_KEY_FILE`, passphrase environment variables, and repository IDs. Several tests intentionally overwrite key blobs, remove files, or inject corrupted key blobs.

Dependencies/integration: depends on archiver fixtures, environment passphrases, repository internals, key serialization, error classes, and binary/non-fork behavior differences. Risks are high around global `os.environ` mutation, content-addressed keyfile names, KDF algorithm preservation, and multi-key ambiguity. Test signals include expected exit codes, exception classes, repository listings, key list rows, and direct key material comparisons.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/key_cmds_test.py -->
