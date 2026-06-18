# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/init.c

Initializer used by httpd magic helper programs after exec. It parses inherited command-line state including buffered input, domain, local port, remote host, scheme, webroot, log fds, netdir, original request line, method, version, URI, and optional search string.

It initializes `HConnect`, input/output `Hio` streams, HTTP formatters, syslog, default remote/domain/webroot values, HTTP version fields, close-after-response behavior, and approximate request time.
