# sources/user-network-fs/rclone/lib/proxy/http.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/http.go -->
## sources/user-network-fs/rclone/lib/proxy/http.go

Purpose: establishes outbound TCP connections through an HTTP or HTTPS proxy using the CONNECT method, optionally chained through another proxy dialer.

Important APIs and control flow: `HTTPConnectDial(network, addr, proxyURL, proxyDialer)` defaults the proxy dialer to `net.Dialer` when nil. If `proxyURL` is nil, it dials `addr` directly. Otherwise it adds a default port to the proxy host, dials the proxy, wraps the connection in TLS for `https` proxy URLs, writes a CONNECT request with optional Basic `Proxy-Authorization`, and reads the proxy response using `http.ReadResponse`. Only `200 OK` succeeds; all failure paths close the connection and wrap context into the error.

State, dependencies, and integration: there is no persistent state. Dependencies include `net`, `net/http`, `net/url`, `crypto/tls`, `bufio`, `base64`, and `golang.org/x/net/proxy`. It integrates with transport construction wherever rclone needs CONNECT tunneling and proxy chaining.

Risks and test signals: credentials are encoded using `proxyURL.User.String()`, which preserves URL escaping semantics and may differ from raw user/password expectations in unusual cases. TLS uses `ServerName` from hostname but otherwise default TLS settings. There are no tests in the requested set for direct dialing, auth header formation, TLS proxy behavior, or response parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/proxy/http.go -->
