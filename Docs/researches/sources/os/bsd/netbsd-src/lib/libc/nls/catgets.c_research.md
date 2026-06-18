# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/catgets.c

Implementation of `_catgets()`. It validates the catalog descriptor, then binary-searches the mapped catalog set table for `set_id` and the message table for `msg_id`.

Catalog numeric fields are read in network byte order with `ntohl()`. On success it returns a pointer into the mapped message text; on missing set/message it sets `errno = ENOMSG` and returns the caller’s fallback string.
