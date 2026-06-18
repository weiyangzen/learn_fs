# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SMBClient.java

Purpose: `SMBClient` is the top-level public client API and connection pool for SMB servers.

Important APIs and control flow: `connect(host)` and `connect(host, port)` look up `host:port`, lease an existing connected `Connection` if possible, otherwise construct and connect a new one. It subscribes to `SMBEventBus`; `ConnectionClosed` removes cached connections and unregisters the server. `close()` force-closes remaining connections.

State, dependencies, and integration: state is held in a concurrent connection table, `ServerList`, `SmbConfig`, and event bus. Connection creation injects config, client, bus, and server list.

Risks: pooling depends on `Connection.lease()` and event delivery; stale connections must be removed reliably. `close()` iterates current values without clearing the map directly. Tests should cover connection reuse, failed connect cleanup, close behavior, event-driven removal, and concurrent connect calls for the same host.
