# File Research: sources/os/plan9/9front/sys/src/cmd/ip/httpd/anonymous.c

HTTPD helper that switches an unauthenticated request into the public web namespace. It binds `webroot` over `/` with `MREPL`, fails with internal error on bind failure, and changes directory to `/`.

This is the minimal namespace-isolation entry point for anonymous web serving.
