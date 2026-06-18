# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create.go

Purpose: Implements LDAP service-account access-key creation and shared create option assembly.

Important APIs/types/functions: `idpLdapAccesskeyCreateFlags`, `idpLdapAccesskeyCreateCmd`, `mainIDPLdapAccesskeyCreate`, `commonAccesskeyCreate`, and `accessKeyCreateOpts`.

Control flow: Requires target and optional target user. It rejects deprecated `--login`, generates missing access/secret keys, validates mutually exclusive `--expiry` and `--expiry-duration`, optionally reads and validates a non-empty policy file, parses expiration by supported local time formats or duration, calls LDAP or generic admin service-account creation, and prints credentials.

State and persistence: Reads optional policy file and creates remote service account credentials.

Dependencies/integration: Uses `newAdminClient`, `madmin.AddServiceAccountReq`, credential generation, policy parser, supported time formats, and shared `accesskeyMessage`.

Risks: Generated secret is printed to output; callers must protect logs. Expiry parsing depends on local timezone. Policy validation happens client-side but enforcement is server-side.

Test signals: No direct tests.
