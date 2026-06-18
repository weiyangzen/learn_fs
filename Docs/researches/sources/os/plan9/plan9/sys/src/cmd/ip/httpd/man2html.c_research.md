# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/man2html.c

Magic helper and standalone converter for Plan 9 manual pages. It serves section indexes, resolves man-page names through `/sys/man/*/INDEX`, handles query-based page and keyword searches, redirects lowercase or directory variants, and rejects `..` in URIs.

Conversion is performed by piping `troff -manhtml` into `troff2html`. In magic mode it validates GET/HEAD and expectations, binds `/usr/web/sys/man` over `/sys/man`, emits HTML response headers, and logs generated output length.
