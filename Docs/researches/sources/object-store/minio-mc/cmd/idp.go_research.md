# Research: sources/object-store/minio-mc/cmd/idp.go

Purpose: top-level command registration for MinIO identity provider management.

Important APIs/types/functions: `idpSubcommands`, `idpCmd`, and `mainIDP`.

Control flow: routes `mc idp` to OpenID or LDAP namespaces, otherwise calls `commandNotFound`.

State and persistence: no direct state changes.

Dependencies/integration points: hooks IDP command tree into the wider `mc` CLI.

Risks: very small but critical command registration file; missing subcommands hide entire IDP feature groups.

Test signals: command-tree smoke tests should assert `openid` and `ldap` are present.
