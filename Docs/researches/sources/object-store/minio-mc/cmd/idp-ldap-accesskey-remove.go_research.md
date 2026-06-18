# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey-remove.go

Purpose: implements `mc idp ldap accesskey remove`/`rm`, deleting an LDAP-linked service account access key.

Important APIs/types/functions: `idpLdapAccesskeyRemoveCmd`, `mainIDPLdapAccesskeyRemove`, and shared `commonAccesskeyRemove`. It uses `madmin.AdminClient.DeleteServiceAccount` and emits `accesskeyMessage`.

Control flow: validates exactly two arguments, target and access key. It creates an admin client for the target alias, deletes the service account by access key, and prints a success message.

State and persistence: mutates server-side service-account state. It does not alter local config.

Dependencies/integration points: shared with OpenID remove through `commonAccesskeyRemove`; uses common CLI globals and admin-client setup.

Risks: the helper intentionally has no LDAP-specific validation, so it will delete any service account visible to the credentials. Callers depend on command path and server authorization to scope behavior.

Test signals: no direct tests; useful tests would mock `DeleteServiceAccount` and validate arity and message emission.
