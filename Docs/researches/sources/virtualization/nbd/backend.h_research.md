# File Research: sources/virtualization/nbd/backend.h

Small backend header declaring:

`void punch_hole(int fd, off_t off, off_t len);`

It is guarded by `NBD_BACKEND_H`. The header relies on includers to have made `off_t` visible.
