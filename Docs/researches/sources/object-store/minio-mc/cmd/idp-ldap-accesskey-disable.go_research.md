# sources/object-store/minio-mc/cmd/idp-ldap-accesskey-disable.go

Purpose: Registers `mc idp ldap accesskey disable`.

Important APIs/types/functions: `idpLdapAccesskeyDisableCmd` and `mainIDPLdapAccesskeyDisable`.

Control flow: The command delegates to `enableDisableAccesskey(ctx, false)`.

State and persistence: Mutates remote service-account status through shared enable/disable code.

Dependencies/integration: Uses global flags and shared LDAP access-key command helpers.

Risks: Validation and error messages are entirely in the shared helper. Usage says `[TARGET]` although implementation expects target plus access key.

Test signals: No direct tests.
