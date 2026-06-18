# File Research: sources/os/bsd/netbsd-src/lib/libpanel/getuser.c

Read completely: 41 lines.

`panel_userptr` returns the panel’s stored user pointer, or null for a null panel.

Security/reliability notes: the API type is `char *`, but the pointer is arbitrary caller-owned data by convention; no ownership is transferred.
