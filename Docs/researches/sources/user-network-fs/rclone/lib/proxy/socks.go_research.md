# sources/user-network-fs/rclone/lib/proxy/socks.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/socks.go -->
## sources/user-network-fs/rclone/lib/proxy/socks.go

Purpose: provides SOCKS5 dialing with optional inline username/password parsing.

Important APIs and control flow: `SOCKS5Dial(network, addr, socks5Proxy, proxyDialer)` defaults to `net.Dialer`, parses `socks5Proxy` as `[user[:password]@]host:port`, constructs a `proxy.Auth` when credentials are present, calls `proxy.SOCKS5("tcp", proxyAddress, proxyAuth, proxyDialer)`, and dials the target `addr` through the returned dialer.

State, dependencies, and integration: no state is retained. It uses simple string splitting plus `golang.org/x/net/proxy`, and integrates with rclone's network transport proxy selection.

Risks and test signals: parsing is intentionally simple and does not URL-decode credentials; usernames or passwords containing `@` or `:` are ambiguous. The SOCKS5 network parameter passed to the proxy server is hardcoded to `"tcp"`, while the final dial uses caller `network`. There are no tests in this group for auth parsing or connection errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/socks.go -->
