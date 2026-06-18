# Research: sources/object-store/minio-mc/cmd/idp-openid-subcommands.go

Purpose: implements OpenID IDP configuration add, update, remove, list, info, enable, and disable, plus shared helpers used by LDAP.

Important APIs/types/functions: `mainIDPOpenIDAddOrUpdate`, `idpRemove`, `idpListCommon`, `idpCfgList`, `idpInfo`, `idpConfig`, and `idpEnableDisable`. Admin APIs include `AddOrUpdateIDPConfig`, `DeleteIDPConfig`, `ListIDPConfig`, and `GetIDPConfig`.

Control flow: add/update parse optional config name when the second arg lacks `=`, join config params, and call OpenID config update. Remove/info/enable/disable accept optional config name. Shared helpers switch between `madmin.OpenidIDPCfg` and `madmin.LDAPIDPCfg`. Listing and info render boxed lipgloss tables, with `_` treated as default config.

State and persistence: add/update/delete/enable/disable mutate server IDP config and may require restart; list/info are read-only.

Dependencies/integration points: central IDP helper implementation for both OpenID and LDAP command files.

Risks: `idpEnableDisable` uses error text saying "remove" even for enable/disable failure. The config body is raw joined CLI input, so quoting and value spaces matter.

Test signals: no direct tests; cover config-name parsing, default `_` rendering, env-origin info markers, and helper behavior for LDAP versus OpenID.
