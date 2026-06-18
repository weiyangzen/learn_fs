# sources/object-store/minio-mc/cmd/config_test.go

Purpose: Tests environment URL parsing used for `MC_HOST_*` alias definitions.

Important APIs/types/functions: `TestParseEnvURLStr` and `TestParseEnvURLStrInvalid`.

Control flow: The main test iterates URL cases with embedded access key, secret key, optional session token, special characters, missing username, missing password, and no credentials. It asserts parsed credential fields plus hostname and port. The invalid test expects an empty string to fail.

State and persistence: No persistent state. The test only exercises parser output.

Dependencies/integration: Uses Go `testing` and `parseEnvURLStr` from `config.go`.

Risks: Does not cover paths, query strings, fragments, non-http schemes, IPv6, percent encoding, or malformed `MC_CONFIG_ENV_FILE` lines.

Test signals: Strong coverage for delimiter ambiguity in secrets and session tokens, which is a key compatibility behavior for env aliases.
