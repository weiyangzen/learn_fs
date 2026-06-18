# sources/object-store/minio/cmd/testdata/config/invalid.yaml

Purpose: negative YAML config fixture for schema/value validation. It keeps the same endpoint topology as valid examples but leaves `version` empty.

Important structure: `version:` has no value. Address, console address, certs dir, pools, and FTP/SFTP options are otherwise syntactically valid.

Control flow and integration: parser tests should reject this file before treating it as a valid server config because the version field is required for config compatibility handling.

State and persistence: static invalid fixture; it should not result in persisted runtime config.

Dependencies: relies on YAML decoding and MinIO's config schema validation.

Risks: if missing version values are accepted silently, future config migrations may lack a reliable format discriminator. Conversely, changing the required version semantics requires adjusting this test fixture.

Test signals: expected failure is missing/invalid config version, not endpoint expansion or service option parsing.
