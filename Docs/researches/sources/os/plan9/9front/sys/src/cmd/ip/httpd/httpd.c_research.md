# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpd.c

Main Plan 9 httpd listener. It parses server options, optionally loads TLS certificate/chain, forks into the background, opens logs and rewrite/content tables, becomes user `none`, then announces an HTTP or HTTPS TCP service.

Each accepted connection is served in a child process with parsed `HConnect` state. Requests pass through magic URI handling, rewrite redirects, virtual-host masquerading, authorization, directory/index normalization, and static file transfer via `sendfd`.

Magic requests under `/magic/<program>/...` exec `/bin/ip/httpd/<program>` with preserved request metadata, buffered input, log descriptors, webroot, netdir, scheme, port, and remote address. Redirect and MIME/state tables are periodically refreshed after batches of accepted connections.
