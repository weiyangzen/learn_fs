# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/init.c

Common initializer used by `/bin/ip/httpd/*` magic helper programs after `httpd.c` execs them. It reconstructs an `HConnect` from command-line arguments: buffered request input, domain, remote address, scheme, port, log fds, netdir, webroot, original request line, method, version, URI, and optional search string.

It installs HTTP formatters, initializes input/output Hio streams, sets conservative defaults, reopens syslog, parses HTTP version text, marks helpers as close-after-response, and approximates request time.
