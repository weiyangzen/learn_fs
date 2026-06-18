# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-create-with-login.go

Purpose: Implements LDAP access-key creation by interactively logging in with LDAP credentials and then creating a service account.

Important APIs/types/functions: `idpLdapAccesskeyCreateWithLoginFlags`, `idpLdapAccesskeyCreateWithLoginCmd`, `mainIDPLdapAccesskeyCreateWithLogin`, and `loginLDAPAccesskey`.

Control flow: The command requires a URL and interactive stdin. It prompts for missing LDAP username/password, creates LDAP STS credentials, fetches temporary credentials, initializes an admin client, builds service-account options with target user set to the temporary access key ID, calls `AddServiceAccountLDAP`, and prints generated credentials.

State and persistence: Reads credentials from flags/stdin and creates remote service-account credentials. No local persistence.

Dependencies/integration: Uses terminal password reading, minio-go LDAP identity credentials, madmin admin client, and shared create flags/options.

Risks: Interactive-only guard rejects non-terminal stdin. Password can still be supplied via CLI flag, which may expose it in shell history/process lists.

Test signals: No direct tests.
