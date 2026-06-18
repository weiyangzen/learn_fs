# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/httpsrv.h

Shared private header for httpd server and magic helper programs. It defines `HSPriv`, rewrite modifier constants, redirect flags, log globals, webroot/netdir globals, and prototypes for allocation, static file serving, content classification, redirects, logging, initialization, hints/stats, and authorization.

This header is the coupling point between the standalone listener, CGI-like `/magic` programs, and common helpers such as `sendfd.c`, `redirect.c`, and `init.c`.
