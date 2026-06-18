# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-list.go

Purpose: implements `mc idp ldap accesskey list`/`ls`, listing LDAP users and their associated STS and service-account access keys.

Important APIs/types/functions: `idpLdapAccesskeyListFlags`, `idpLdapAccesskeyListCmd`, `mainIDPLdapAccesskeyList`, and shared `commonAccesskeyList`. The command calls `madmin.AdminClient.ListAccessKeysLDAPBulkWithOpts` and prints `userAccesskeyList` messages with `LDAP: true`.

Control flow: `commonAccesskeyList` validates arguments, parses `TARGET[:CFGNAME]`, resolves users and list flags, and creates `madmin.ListAccessKeysOpts`. With no user, `--self`, or `--all`, it tentatively sets `All` and allows an Access Denied retry as self for backward compatibility. `mainIDPLdapAccesskeyList` creates an admin client, calls the LDAP bulk listing API, retries if needed, and prints one message per DN.

State and persistence: read-only against MinIO server identity data. No local persistence.

Dependencies/integration points: relies on `newAdminClient`, `globalContext`, `fatalIf`, `probe`, `madmin.ListAccessKeysOpts`, and shared output types from other access-key files.

Risks: flag error text says `--permanent-only` while the actual flag is `--svcacc-only`; exact string matching on `"Access Denied."` is brittle. `commonAccesskeyList` is shared by OpenID, so changes affect both IDP families.

Test signals: no direct tests in this file; coverage should exercise flag exclusivity, target config-name parsing, tentative all retry, and LDAP message shape.
