# Research: sources/object-store/minio-mc/cmd/idp-ldap-accesskey.go

Purpose: registers the `mc idp ldap accesskey` command namespace.

Important APIs/types/functions: `idpLdapAccesskeySubcommands`, `idpLdapAccesskeyCmd`, and `mainIDPLDAPAccesskey`. The namespace includes list, remove, info, create, create-with-login, edit, enable, disable, and STS revoke.

Control flow: CLI framework dispatches to subcommands. If invoked without a matching subcommand, `mainIDPLDAPAccesskey` delegates to `commandNotFound`.

State and persistence: no direct state changes. Persistence is delegated to subcommands.

Dependencies/integration points: depends on subcommand variables declared across LDAP access-key files, `globalFlags`, and `setGlobalsFromContext`.

Risks: adding or removing a subcommand here directly changes CLI discoverability. Hidden or missing commands can make implemented functionality unreachable.

Test signals: no direct tests; smoke tests should assert command registration and help output.
