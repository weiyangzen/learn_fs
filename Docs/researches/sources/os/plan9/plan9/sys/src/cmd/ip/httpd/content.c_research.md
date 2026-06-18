# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/content.c

MIME/content classification support for httpd. `contentinit` tracks `/sys/lib/mimetype` by qid, reloads it when changed, strips comments, and builds a suffix table containing type, subtype, and optional encoding.

`uriclass` classifies by filename suffix chain, including encodings such as compressed extensions, while `dataclass` sniffs an initial data buffer and returns `text/plain` only if the bytes are printable valid UTF.
