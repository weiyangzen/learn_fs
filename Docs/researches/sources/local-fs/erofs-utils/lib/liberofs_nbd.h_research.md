# File Research: sources/local-fs/erofs-utils/lib/liberofs_nbd.h

This header defines userspace Network Block Device integration declarations.

Key definitions:
- `EROFS_NBD_MAJOR` is 43.
- Request command enum covers read, write, disconnect, flush, trim, and write-zeroes.
- `struct erofs_nbd_request` mirrors packed NBD request layout with magic, type, cookie/handle, offset, and length.
- `EROFS_NBD_DEAD_CONN_TIMEOUT` is 30 days for recovery behavior.

Classic ioctl/socket style API:
- `erofs_nbd_in_service()`
- `erofs_nbd_devscan()`
- `erofs_nbd_connect()`
- `erofs_nbd_get_identifier()`
- `erofs_nbd_get_index_from_minor()`
- `erofs_nbd_do_it()`
- `erofs_nbd_get_request()`
- `erofs_nbd_send_reply_header()`
- `erofs_nbd_disconnect()`

Netlink API:
- `erofs_nbd_nl_connect()`
- `erofs_nbd_nl_reconnect()`
- `erofs_nbd_nl_reconfigure()`
- `erofs_nbd_nl_disconnect()`

Risk / note:
- The struct uses mixed endian fields and packed layout; implementation must preserve kernel ABI exactly.
