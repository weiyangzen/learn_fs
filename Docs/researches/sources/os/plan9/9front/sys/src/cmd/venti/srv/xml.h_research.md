# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/xml.h

`xml.h` declares XML rendering functions for `AMap`, `Arena`, and `Index`, plus lower-level helpers for names, scores, booleans, integers, and indentation.

It is a small contract between XML object renderers in `xml.c` and HTTP/XML primitive functions elsewhere in the Venti server.
