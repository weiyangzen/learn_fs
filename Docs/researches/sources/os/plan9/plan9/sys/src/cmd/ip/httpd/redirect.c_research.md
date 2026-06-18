# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/redirect.c

Rewrite-table loader and lookup engine for httpd. `redirectinit` monitors `/sys/lib/httpd.rewrite` by qid, strips comments, and rebuilds separate hash tables for URI redirects and virtual-host-to-webroot-prefix mappings.

Replacement fields may be decorated for silent, permanent, subordinate, or exact-only behavior. `redirect` finds the longest path prefix match and constructs a per-request replacement path or URL; `masquerade` maps Host headers to implicit webroot prefixes.
