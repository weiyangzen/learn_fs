# File Research: sources/virtualization/nbd/man/nbd-server.5.sgml.in

DocBook manpage template for the `nbd-server` configuration file.

It defines the config file grammar: `[generic]` must be first, other sections define exports, comments occupy whole/comment lines, and option lines use `name = value` with string/integer/boolean values.

Generic options include export listing, TLS CA/cert/key, forced TLS mode, user/group privilege drop, include directory, listen address, max worker threads, obsolete oldstyle handling, default port, splice, Unix socket/dual listen, and GnuTLS priority.

Export options include authorization file, copy-on-write, COW directory, backend export file path, fixed file size, flush, per-export TLS requirement, FUA, max connections, multifile, treefiles, pre/post run hooks, read-only, rotational flag, SDP, sparse COW, sync, temporary exports, timeout, transaction log, trim, virtualization style, TLS-only, and waitfile migration support.

The virtualization section defines filename mapping based on client address with `none`, `ipliteral`, `iphash`, and `cidrhash`. The waitfile section describes accepting writes into a diff file before the backend arrives, then merging on SIGUSR1 for live migration.
