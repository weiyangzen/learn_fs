# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getnattype.c

This helper maps a NAT runtime entry’s `nat_redir` bitmask to a display string.

It recognizes MAP, MAP-BLOCK, RDR, rewrite map/redirect, BIMAP, divert map/redirect, and encapsulation map/redirect forms. Unknown bit patterns are formatted into a static buffer as `unknown(...)`.

It returns `???` for a null NAT pointer.
