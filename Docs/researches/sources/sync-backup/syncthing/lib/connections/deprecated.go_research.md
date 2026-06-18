# sources/sync-backup/syncthing/lib/connections/deprecated.go

## sources/sync-backup/syncthing/lib/connections/deprecated.go

Purpose: Registers deprecated KCP connection schemes as explicitly invalid listener/dialer factories.

Important APIs/types/functions: `invalidListener` and `invalidDialer` embed the normal factory interfaces and implement `Valid(config.Configuration) error`. `init` registers `kcp`, `kcp4`, and `kcp6` in both factory maps with `errDeprecated`.

Control flow and state: Factory lookup for these schemes returns a factory whose `Valid` method always errors, defaulting to `errUnsupported` if no explicit error is configured.

Dependencies and integration: Uses the global `listeners` and `dialers` registries from the connections package and `config.Configuration` for interface compatibility.

Risks and test signals: Keeps deprecated protocols recognizable so users get a deprecation error instead of a generic unsupported error. `TestGetDialer` validates KCP returns `errDeprecated`.
