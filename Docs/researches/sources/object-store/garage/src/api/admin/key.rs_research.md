# sources/object-store/garage/src/api/admin/key.rs

Purpose: implements S3 access-key administration: list, lookup, create, import, update, delete, and detailed key info with related bucket permissions and aliases.

Important handlers/functions: `ListKeysRequest`, `GetKeyInfoRequest`, `CreateKeyRequest`, `ImportKeyRequest`, `UpdateKeyRequest`, `DeleteKeyRequest`, `key_info_results`, and `apply_key_updates`.

Control flow and state: key records are persisted in `garage.key_table`. Creation generates a new key and returns secret material in the detail response. Import rejects any existing record for the supplied access key ID, even deleted ones, validates key format through `Key::import`, and stores the imported key. Update mutates CRDT fields for name, expiration, and create-bucket permission. Delete uses `locked_helper` so associated bucket permissions/aliases can be cleaned consistently. `key_info_results` joins authorized bucket IDs and local aliases to bucket table state and optionally includes the secret key.

Dependencies/integration: uses Garage key model, bucket table, locked helper, permission expiration type, table range/get/insert APIs, chrono conversion, and admin schema types.

Risks: secret key exposure depends on `show_secret` and creation/import choices; callers must avoid logging responses. Search must resolve exactly one key. Import cannot reuse deleted key IDs, which avoids resurrection ambiguity but may surprise users. Timestamp conversion panics on invalid stored milliseconds. Update `allow`/`deny` only affects `create_bucket`; bucket-specific permissions are managed in `bucket.rs`.

Test signals: cover list filtering of deleted keys, lookup by ID/search/no match/multiple matches, create with secret returned, import invalid/existing/deleted key IDs, expiration vs never-expire conflict, allow/deny create-bucket transitions, delete cleanup via helper, and `show_secret_key` response behavior.
