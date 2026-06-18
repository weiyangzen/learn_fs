# File Research: sources/virtualization/nbd/man/nbdtab.5.sgml.in

DocBook manpage template for `nbdtab(5)`, the client-side predefined connection file.

It documents one connection definition per line with four fields: short device name without `/dev/`, server hostname or Unix socket path, export name, and optional comma-separated options.

Documented options mirror client options relevant to stored device profiles: block size, CA/cert/key files, connection count, no-optgo, persist, port, GnuTLS priority, swap, timeout, TLS hostname, and Unix socket mode. Unknown options warn unless prefixed with `_`, which is reserved for local/distribution customization.

The example shows two device entries, including a swap/persist entry.
