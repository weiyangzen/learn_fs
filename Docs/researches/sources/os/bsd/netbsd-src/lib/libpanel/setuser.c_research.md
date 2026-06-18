# File Research: sources/os/bsd/netbsd-src/lib/libpanel/setuser.c

Read completely: 42 lines.

`set_panel_userptr` stores a caller-supplied pointer in the panel’s `user` field and returns `OK`; it returns `ERR` for null panels.

Security/reliability notes: no allocation or ownership management is performed.
