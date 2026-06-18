# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/hints.c

Prefetch hint subsystem for httpd. It loads `/sys/log/httpd/url` into hash-indexed URL tables and `/sys/log/httpd/pathstat` into compact per-URL hint arrays, refreshing only when file length changes and files are old enough to be stable.

`urlcanon` normalizes URL paths and applies site-specific Bell Labs rewrites. `hintprint` looks up likely next URLs, filters by probability threshold and already-held client hints, stats files under `webroot`, and emits `Fresh:` headers with probability, ETag, size class, and path.
