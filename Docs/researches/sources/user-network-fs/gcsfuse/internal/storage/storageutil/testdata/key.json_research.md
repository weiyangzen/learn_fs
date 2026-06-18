## sources/user-network-fs/gcsfuse/internal/storage/storageutil/testdata/key.json

Purpose: Minimal service-account-style JSON fixture for auth tests.

Important APIs/types/functions: contains standard service account fields including `type`, `project_id`, private key metadata placeholders, token/auth URLs, client IDs, cert URLs, and `universe_domain`.

Control flow: consumed by auth credential loaders in tests; not executable code.

State and persistence behavior: static testdata file. It must not contain real secrets; all values are placeholders.

Dependencies and integration points: used by `CreateTokenSource`, `GetClientAuthOptionsAndToken`, and storage handle auth tests.

Risks: auth library validation requirements can change and reject placeholder private key material. Any accidental replacement with real credentials would be a security incident.

Test signals: successful auth-helper tests confirm the fixture remains structurally acceptable for local credential parsing.
