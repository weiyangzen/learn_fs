# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/sendfd.c

Static-file response engine for httpd. It classifies content from URI suffix or data sniffing, generates ETags from qid path/version, checks Accept/Content-Encoding, conditional request headers, and If-Range, then emits 200, 206, 304, 406, 412, or 416 responses.

It supports HEAD, full-body transfer, single byte ranges, and multipart byte ranges with MIME boundaries. `fixrange` normalizes suffix ranges, clamps ranges to file length, removes invalid ranges, and merges adjacent/overlapping ranges while preserving request order where possible.
