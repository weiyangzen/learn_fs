# sources/sync-backup/syncthing/lib/config/ldaptransport.go

## sources/sync-backup/syncthing/lib/config/ldaptransport.go

Purpose: Encodes LDAP transport mode as text in configuration.

Important APIs/types/functions: `LDAPTransport` supports `plain`, `tls`, and `starttls`; methods are `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Unknown text defaults to `LDAPTransportPlain`; unknown enum values stringify as `unknown`.

Dependencies and integration: Used by `LDAPConfiguration.Transport` and LDAP authentication setup outside this subset.

Risks and test signals: Defaulting unknown values to plain transport may be compatibility-friendly but less secure than failing closed. No direct tests here; configuration default tests cover struct initialization.
