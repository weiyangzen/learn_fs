## sources/sync-backup/syncthing/lib/netutil/netutil.go

Purpose: network helpers for URL-like address construction and default gateway discovery.

Important APIs: `AddressURL(network, host)` builds a URL string with the network as scheme and host as host. `Gateway` returns the default gateway from `github.com/jackpal/gateway`, with Android-oriented environment fallback `FALLBACK_NET_GATEWAY_IPV4`.

Control flow and state: `AddressURL` constructs a `url.URL` and returns its string. `Gateway` calls `gateway.DiscoverGateway`; on error it checks the fallback environment variable, validates it with `net.ParseIP`, and returns either the parsed IP or an invalid-IP error.

Dependencies and integration points: `pmp.Discover` uses `Gateway` to instantiate a NAT-PMP client. Address URL helpers can be used by listener/dialer configuration formatting.

Risks: environment fallback trusts process environment and only validates parseability, not reachability. Gateway discovery can fail on Android 14+ due to `/proc/net/route` restrictions. `AddressURL` does not validate schemes or hosts.

Test signals: `netutil_test.go` covers basic URL construction.
