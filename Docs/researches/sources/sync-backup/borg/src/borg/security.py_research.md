# sources/sync-backup/borg/src/borg/security.py

Purpose: persists and checks repository trust metadata to detect relocation, encryption method changes, manifest replay, and unknown unencrypted repository access.

Important APIs/types: `SecurityManager` stores `key-type`, `location`, and `manifest-timestamp` in a security directory. It exposes `known`, `key_matches`, `save`, location/key/replay assertions, `assert_access_unknown`, `assert_secure`, and `destroy`. Module-level `assert_secure` is a convenience wrapper.

Control flow/state: `assert_secure` handles unknown unencrypted access first, then checks location, key type, and manifest timestamp. Relocation and unknown unencrypted access prompt with env-var overrides. Accepted relocation updates stored location. Replay raises `RepositoryIDNotUnique` for plaintext keys and `RepositoryReplay` for encrypted keys.

Persistence: security state lives outside the repo in `get_security_dir(repository.id_str, legacy=...)` and is written atomically with `SaveFile`.

Dependencies/integration: uses repository ID/version/location, manifest timestamp/key, `PlaintextKey`, `yes`, and platform `SaveFile`.

Risks: timestamp comparison relies on sortable timestamp strings. Read errors degrade to warnings and empty values. Environment overrides can bypass safeguards. Security directory loss causes relearning.

Test signals: first save, relocation accept/deny, env overrides, key mismatch, replay detection, unencrypted unknown prompt, read errors, and legacy directory selection.
