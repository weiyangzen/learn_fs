# Research: sources/object-store/minio-mc/cmd/idp-ldap.go

Purpose: registers the `mc idp ldap` namespace.

Important APIs/types/functions: `idpLdapSubcommands`, `idpLdapCmd`, and `mainIDPLdap`. The namespace includes configuration, policy, and access-key commands.

Control flow: normal CLI subcommand dispatch, with `commandNotFound` fallback.

State and persistence: no direct state changes.

Dependencies/integration points: integrates LDAP command groups under the top-level IDP command.

Risks: this file is the discoverability point for LDAP policy and access-key functionality; omission breaks CLI reachability.

Test signals: no direct tests; command-tree smoke tests should validate subcommand registration.
