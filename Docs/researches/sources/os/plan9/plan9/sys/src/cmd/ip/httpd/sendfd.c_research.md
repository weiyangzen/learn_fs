# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/sendfd.c

Static-file response engine for httpd. It classifies content by URI suffix or data sniffing, generates ETags from qid path/version, checks Accept and Content-Encoding, evaluates conditional request headers, handles If-Range, and emits 200, 206, 304, 406, 412, or 416 responses.

It supports HEAD, full transfers, single ranges, and multipart byte ranges with MIME boundaries. `fixrange` normalizes suffix ranges, clamps to file length, drops invalid ranges, and merges adjacent/overlapping ranges while keeping useful request order.
