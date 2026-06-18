## sources/sync-backup/syncthing/lib/osutil/ping.go

Purpose: TCP latency measurement helpers.

Important APIs: `TCPPing(ctx, address)` measures time to establish a TCP connection and closes it. `GetLatencyForURL(ctx, addr)` parses a URL string and delegates to `TCPPing` on the URL host.

Control flow and state: `TCPPing` records start time, uses `net.Dialer.DialContext`, closes on success, and returns elapsed time. `GetLatencyForURL` uses `url.Parse` and passes `u.Host`.

Dependencies and integration points: used by connection/address selection or diagnostics that rank endpoints by TCP connect latency.

Risks: measures connect time only, not TLS/BEP latency. URL strings without a host produce dial errors. Context controls timeout/cancel behavior.

Test signals: no direct tests in this subset.
