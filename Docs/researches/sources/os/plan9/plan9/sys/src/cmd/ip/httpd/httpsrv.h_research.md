# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/httpsrv.h

Shared private header for the httpd listener and magic helper programs. It defines `HSPriv`, timeout and redirect modifier constants, redirect flags, global log/webroot/netdir state, allocation helpers, static-file functions, MIME functions, init, redirect, logging, authorization, anonymous namespace, and hint prototypes.

This is the coupling point between the standalone listener, `/magic` programs, and common support modules.
