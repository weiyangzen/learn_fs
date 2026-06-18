# File Research: sources/os/bsd/freebsd-src/sys/sys/khelp.h

Defines the kernel helper module KPI used with `hhook.h`. Helper classes currently cover TCP and socket helpers.

Public routines register/deregister helpers, initialize/destroy helper OSD storage, fetch helper OSD data by id, resolve helper ids by name, and add/remove helper hook registrations. This is the management layer above helper hook execution.
