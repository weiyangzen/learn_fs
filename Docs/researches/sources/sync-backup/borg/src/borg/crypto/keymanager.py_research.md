# sources/sync-backup/borg/src/borg/crypto/keymanager.py

Purpose: implements high-level key export/import workflows, including normal keyfiles, QR HTML export, paper key export, and interactive paper key import.

Important APIs: `sha256_truncated(data, num)` makes short checksums. `KeyManager(repository)` identifies the repository key class from the manifest and rejects unencrypted repositories. `_list_borg_keys()` enumerates key blobs and labels without decrypting. `load_keyblob(label=None, key_id=None)` selects exactly one key for export. `store_keyblob(args)` writes imported key data to keyfile or repo storage according to `--key-location` or default. `get_keyfile_data`, `store_keyfile`, `export`, `export_qr`, `export_paperkey`, `import_keyfile`, and `import_paperkey` implement the concrete formats.

Control flow and state: `self.keyblob` holds base64 key payload text selected or imported. Export formats wrap it with `BORG_KEY <repoid>` as needed. Paper export decodes base64 to binary, emits an ID line with line count/repo ID/checksum, then numbered 18-byte hex lines with per-line checksums. Paper import loops until checksums and repo ID match, then stores the reconstructed base64 blob.

Dependencies and integration: uses `RepoObj.extract_crypted_data` and `identify_key` to determine crypto/key storage support; reuses keyfile helpers from `crypto.key`; accesses repository key APIs; uses `dash_open`, `yes`, keys dir helpers, `paperkey.html` package data, and `KEY_LOCATIONS`.

Risks: importing a valid key into the wrong repository is guarded by repo ID checks. Multiple-key repositories require an unambiguous selector for export. `store_keyblob` uses `CHPOKey` only to reuse target lookup for keyfile storage, which is a coupling to FlexiKey behavior. Paper import is interactive and must handle aborts without partial state.

Test signals: cover unencrypted repo rejection, single and multi-key selection by label/key prefix, ambiguous selector errors, keyfile export/import repo mismatch, QR export insertion, paper export checksums, paper import retry/abort paths, key-location storage choices, and corrupted key envelope visibility.
