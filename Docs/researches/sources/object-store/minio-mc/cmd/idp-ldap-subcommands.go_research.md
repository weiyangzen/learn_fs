# Research: sources/object-store/minio-mc/cmd/idp-ldap-subcommands.go

Purpose: implements LDAP IDP configuration add, update, remove, list, info, enable, and disable commands.

Important APIs/types/functions: `mainIDPLDAPAdd`, `mainIDPLDAPUpdate`, `mainIDPLDAPRemove`, `mainIDPLDAPList`, `mainIDPLDAPInfo`, `mainIDPLDAPEnable`, and `mainIDPLDAPDisable`. It reuses OpenID-shared helpers `idpRemove`, `idpListCommon`, `idpInfo`, and `idpEnableDisable`.

Control flow: add/update parse `TARGET [CFG_PARAMS...]`, enforce LDAP default config only, join remaining `key=value` parameters into a config body, and call `AddOrUpdateIDPConfig` with `madmin.LDAPIDPCfg`. Remove/list/info require one target and call shared helpers. Enable/disable also require one target and write `enable=` or `enable=off` through the shared helper.

State and persistence: mutates MinIO server IDP configuration. Server may return a restart requirement, surfaced via `configSetMessage`.

Dependencies/integration points: depends on `madmin.LDAPIDPCfg`, admin-client creation, shared IDP helpers, and global CLI setup.

Risks: this file rejects named LDAP configs by design, so future server support for named LDAP configs requires coordinated changes. Joining raw args into one config string preserves existing config API behavior but makes shell quoting important.

Test signals: no direct tests; important cases include named-config rejection, update versus add flag, and restart message propagation.
