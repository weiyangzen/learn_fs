## sources/sync-backup/syncthing/lib/connections/service.go

Purpose: Central connection manager that supervises listeners, dials configured devices, performs TLS/device identity validation and Hello exchange, tracks active connections, updates metrics, emits address-change events, and exposes connection/listener status.

Important APIs/types/functions: Public `Service` interface; `NewService`; status structs; `handleConns`, `handleHellos`, `connect`, `dialDevices`, `resolveDialTargets`, `CommitConfiguration`, `AllAddresses`, `ExternalAddresses`, `ListenerStatus`, `ConnectionStatus`, `NATType`; helpers `getDialerFactory`, `getListenerFactory`, `tlsTimedHandshake`, `IsAllowedNetwork`, `dialParallel`, `validateIdentity`; `nextDialRegistry`; `deviceConnectionTracker`; `newConnectionID`.

Control flow: Construction subscribes to config, starts listeners/NAT service, and adds three service loops. Listener/dialer paths feed `internalConn` into `handleConns`, which verifies TLS protocol/certificate count, rejects self/ignored/paused/over-limit/disallowed/low-priority connections, then exchanges BEP Hello asynchronously. `handleHellos` processes the exchange, calls model `OnHello`, validates configured certificate name, wraps traffic limiters, creates a protocol connection, tracks it, schedules redial on close, and hands it to the model. The connect loop repeatedly resolves configured device addresses, consults discovery for `dynamic`, filters by allowed networks and priority cutoffs, schedules backoff in `nextDialRegistry`, sorts dial queues, and dials targets in parallel with global and per-device semaphores.

State and persistence: Process state includes listener maps/tokens, status maps, dial-now channel and per-device set, next-dial cooldown registry, limiter, NAT service, and tracked protocol connections/wanted counts. No direct disk persistence; config wrapper is external.

Dependencies and integration points: Integrates config subscriptions, discovery lookups, NAT/UPnP/PMP providers, relay/TCP/QUIC factories, protocol connection/model interfaces, Prometheus metrics, event logger, TLS, semaphores, and suture supervision.

Risks: This is highly concurrent: listener map locks, connection tracker locks, dial cancellation, Hello goroutines, and config callbacks must stay ordered. Identity validation is security-sensitive. Priority/upgrade logic can churn connections if thresholds or desired connection negotiation are wrong. `IsAllowedNetwork` only supports resolvable IP/CIDR rules and ignores malformed CIDRs. Timer handling in connection loop must avoid leaks and rapid loops.

Test signals: Existing tests outside this item cover fixup/allowed networks/dialer selection/connection status/registry cleanup/connection establishment. Files in this item add limiter and registry unit coverage.
