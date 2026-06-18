# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/man2html.c

Magic helper and standalone converter for Plan 9 manual pages. It can convert a direct man-page URI using `troff -manhtml | troff2html`, serve section indexes, look up page names through `/sys/man/*/INDEX`, and handle query-based man or keyword searches.

It rejects `..` in man-page URIs, redirects directories and lowercase variants, binds `/usr/web/sys/man` onto `/sys/man`, and emits HTML search/result pages. In magic mode it validates GET/HEAD and expectation headers, then logs generated output length.
