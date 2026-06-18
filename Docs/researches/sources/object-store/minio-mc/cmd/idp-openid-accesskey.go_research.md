# Research: sources/object-store/minio-mc/cmd/idp-openid-accesskey.go

Purpose: registers `mc idp openid accesskey`.

Important APIs/types/functions: `idpOpenidAccesskeySubcommands`, `idpOpenIDAccesskeyCmd`, and `mainIDPOpenIDAccesskey`.

Control flow: dispatches to list, remove, info, edit, enable, or disable; unknown commands route to `commandNotFound`.

State and persistence: none directly.

Dependencies/integration points: integrates OpenID access-key wrappers under OpenID IDP command.

Risks: no create command is included for OpenID here, unlike LDAP; that is a product/CLI surface distinction.

Test signals: command-tree tests should verify the intended subcommand set.
