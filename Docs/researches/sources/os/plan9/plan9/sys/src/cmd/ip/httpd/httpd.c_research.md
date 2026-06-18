# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpd.c

Main Plan 9 httpd listener. It parses certificate, namespace, address, domain, and webroot options; daemonizes; opens logs and rewrite/content/hint tables before namespace reduction; becomes user `none`; and announces HTTP or HTTPS service.

Each accepted connection runs in a forked child, optionally wrapped with TLS. Requests flow through overload throttling, request parsing, `/magic` extraction, rewrite/virtual-host redirects, header parsing, directory/index normalization, `.httplogin` authorization, and `sendfd` static transfer.

Magic requests exec `/bin/ip/httpd/<program>` with reconstructed request state, buffered input, log descriptors, remote address, netdir, scheme, port, webroot, method, version, URI, and query string. Parent processes periodically refresh redirects, MIME tables, and prefetch hint databases.
