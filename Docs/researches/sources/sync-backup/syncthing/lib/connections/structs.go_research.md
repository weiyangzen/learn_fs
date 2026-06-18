## sources/sync-backup/syncthing/lib/connections/structs.go

Purpose: Defines shared connection abstractions, transport metadata, listener/dialer interfaces, model interface, address-change notification, and dial target wrapper.

Important APIs/types/functions: `tlsConn`, `internalConn`, `connType`, `newInternalConn`, `internalConn` methods (`Close`, `Type`, `IsLocal`, `Priority`, `Crypto`, `Transport`, `EstablishedAt`, `ConnectionID`, `String`, `LogValue`), `dialerFactory`, `commonDialer`, `genericDialer`, `listenerFactory`, `ListenerAddresses`, `genericListener`, `Model`, `onAddressesChangedNotifier`, and `dialTarget`.

Control flow: Dialers/listeners wrap raw TLS-like connections in `internalConn`. `Close` sets a short write deadline before closing to avoid blocking on TLS close alerts. `Transport` enriches transport with IPv4/IPv6 suffix when the remote address can be parsed. `commonDialer.Priority` uses `lanChecker` to choose LAN/WAN priorities. Notifier invokes registered callbacks with listener addresses or clears them on shutdown.

State and persistence: `internalConn` carries per-connection metadata and a post-Hello connection ID. Notifier stores callback slices. No persistence.

Dependencies and integration points: Used throughout all transport adapters and the central service; imports config, registry, NAT, protocol, stats, suture, and osutil.

Risks: `Crypto` assumes TLS suite/version maps contain the negotiated values; unknown values format empty names. Callback list is not mutex-protected, so registration is expected before concurrent notifications.

Test signals: Indirectly tested by connection establishment, status, and logging behavior.
