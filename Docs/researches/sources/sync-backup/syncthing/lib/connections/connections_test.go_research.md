# sources/sync-backup/syncthing/lib/connections/connections_test.go

## sources/sync-backup/syncthing/lib/connections/connections_test.go

Purpose: Tests connection utility behavior, factory selection, connection status bookkeeping, next-dial cooldown cleanup, and real TCP/QUIC connection establishment.

Important APIs/types/functions: Tests `fixupPort`, `IsAllowedNetwork`, `getDialerFactory`, `getListenerFactory`, `connectionStatusHandler`, `nextDialRegistry.sleepDurationAndCleanup`, and data transfer through `withConnectionPair`. Helpers build TLS certs, suture supervisors, NAT service, listener/dialer factories, registries, and LAN checkers.

Control flow and state: Factory tests parse URIs and verify deprecated, disabled, invalid, and supported schemes. Connection status tests ensure `context.Canceled` does not overwrite meaningful errors. Next-dial tests simulate timestamps and attempt counts to verify registry cleanup. Establishment tests start a listener, wait for a concrete LAN address, dial it, trigger QUIC stream setup with an initial write, then verify data transfer.

Dependencies and integration: Integrates `config`, `registry`, `nat`, `protocol`, `tlsutil`, `suture`, network sockets, and connection factories from files outside this subset. Benchmarks optionally use a local relay.

Risks and test signals: Real network tests can be timing-sensitive, especially QUIC/relay registration. Coverage protects default port fixups, CIDR allow/deny order, deprecated KCP rejection, disabled relay behavior, cooldown pruning, and basic encrypted transport functionality.
