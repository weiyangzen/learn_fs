# sources/sync-backup/syncthing/lib/config/ldapconfiguration.go

## sources/sync-backup/syncthing/lib/config/ldapconfiguration.go

Purpose: Defines LDAP authentication configuration for the GUI.

Important APIs/types/functions: `LDAPConfiguration` contains server address, bind DN, transport, TLS verification skip flag, search base DN, and search filter. `Copy` returns the value unchanged.

Control flow and state: Pure data holder; defaults are supplied by `structutil` through struct tags when the root configuration is loaded or created.

Dependencies and integration: Used by `GUIConfiguration.AuthMode == AuthModeLDAP` and wrapper accessors. It depends on `LDAPTransport` for transport encoding.

Risks and test signals: `InsecureSkipVerify` is security-sensitive. There are no direct tests in this subset beyond default/copy behavior through configuration load and wrapper methods.
