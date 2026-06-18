# File Research: sources/os/plan9/9front/sys/src/cmd/ip/hproxy.c

Small HTTP proxy and CONNECT tunnel. It reads the request headers, strips `Connection` and `Proxy-Connection`, parses the target URL or host form including bracketed IPv6, dials the destination, and relays data in both directions via forked copy loops.

For CONNECT it returns `200 Connection Established` or `500 Connection Failed`; for normal HTTP it rewrites the request line to origin-form and forces `Connection: close`.

It uses a 30-second dial alarm and kills the process group when either relay side exits.
