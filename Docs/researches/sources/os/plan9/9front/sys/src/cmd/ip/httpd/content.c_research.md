# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/content.c

HTTP content classification helper. `contentinit` reads `/sys/lib/mimetype`, tracks qid changes, and rebuilds a linked list of suffix-to-content-type/content-encoding mappings.

`uriclass` walks suffixes from a URI filename and returns first matching media type and encoding. `dataclass` classifies a byte buffer as `text/plain` only if it is valid text/UTF and contains no disallowed control bytes; otherwise it leaves type unknown.

Uses HTTPD allocation/content constructors (`hstrdup`, `hmkcontent`) and local fatal allocation helpers.
