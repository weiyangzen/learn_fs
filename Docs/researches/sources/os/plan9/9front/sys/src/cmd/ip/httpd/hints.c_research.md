# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/hints.c

HTTPD prefetch-hints support. It reads `/sys/log/httpd/url` into URL hash tables and `/sys/log/httpd/pathstat` into per-URL hint arrays, refreshing only when files change and are older than 300 seconds.

`urlcanon` normalizes repeated/trailing slashes and applies Bell Labs site-specific path rewrites. `hintprint` emits `Fresh:` headers for likely next resources above a probability threshold, excluding hints the client already reports having, and includes ETag-like qid/version tags plus logarithmic size estimates.

The implementation uses fixed `URLmax` tables, custom hash chaining, and arena allocation for compact refresh/rebuild behavior.
