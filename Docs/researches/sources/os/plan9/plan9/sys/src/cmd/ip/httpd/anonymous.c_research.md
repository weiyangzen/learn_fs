# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/httpd/anonymous.c

Common helper for httpd magic programs. It binds `webroot` over `/` with `MREPL`, changes to `/`, and returns HTTP internal failure if the anonymous web namespace cannot be installed.
