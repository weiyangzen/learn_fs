# sources/sync-backup/syncthing/lib/stun/stun.go

Purpose: runs STUN discovery/keepalive to classify NAT type and publish external UDP address changes.

Important APIs and control flow: `New` wraps a supplied `net.PacketConn` in a go-stun client and records a service name from the local address. `Serve` loops until context cancellation, respecting dynamic config disablement, iterating configured STUN servers, and sleeping for `stunRetryInterval` after failures or non-punchable NAT. `runStunForServer` resolves the server, runs `client.Discover` through `svcutil.CallWithContext`, filters unusable NAT results, notifies NAT type, and starts keepalive only for punchable NAT types. `stunKeepAlive` adapts keepalive sleep based on observed external port changes and aborts below the configured minimum. Subscriber callbacks are only fired on changes.

State and persistence: stores current NAT type and external host in memory. No durable state.

Dependencies and integration: depends on `github.com/ccding/go-stun/stun`, config options, and subscriber methods likely implemented by connection services/discovery.

Risks: no mutex protects `natType`/`addr`; service appears single-threaded except callbacks. `CallWithContext` cannot stop an underlying blocked STUN call, only returns early. Adaptive keepalive may be sensitive to config extremes. No local tests in this subset.
