# Research: sources/object-store/minio-mc/cmd/idp-ldap-policy.go

Purpose: registers `mc idp ldap policy` as the LDAP policy assignment namespace.

Important APIs/types/functions: `idpLdapPolicySubcommands`, `idpLdapPolicyCmd`, and `mainIDPLDAPPolicy`.

Control flow: CLI dispatches to attach, detach, and entities. Unknown or absent subcommands route through `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: depends on policy subcommand definitions, `globalFlags`, and common command setup.

Risks: namespace wiring is simple, but missing entries make implemented policy operations unreachable.

Test signals: no direct tests; command registration/help tests are sufficient.
