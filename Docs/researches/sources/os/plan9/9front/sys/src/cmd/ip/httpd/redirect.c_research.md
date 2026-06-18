# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/redirect.c

Rewrite-table loader and lookup engine for httpd. `redirectinit` reads `/sys/lib/httpd.rewrite`, tracks qid changes, strips comments, and populates separate hash tables for URI redirects and virtual-host-to-webroot-prefix mappings.

Replacement prefixes may be decorated with silent, permanent, subordinate, or exact-only modifiers. `redirect` finds the longest path prefix match and returns a per-request allocated replacement; `masquerade` maps Host headers to implicit webroot subdirectories.
