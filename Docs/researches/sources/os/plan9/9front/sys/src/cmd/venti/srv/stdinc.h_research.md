# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/stdinc.h

`stdinc.h` is the common include bundle for Venti server sources. It pulls in Plan 9 libc, libventi, flate, libsec, thread, httpd, draw, and memdraw headers.

The file is intentionally small and acts as a precompiled-style local convention: most server files include it before `dat.h` and `fns.h` to get shared system types and APIs.
