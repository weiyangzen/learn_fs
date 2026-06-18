# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_util.h

Defines basic libisns utility macros and prototypes. Byte-order macros map directly to `<arpa/inet.h>` functions, allocation maps to `malloc/free`, and `ARRAY_ELEMS()` computes static array size.

It declares pipe command helpers, kqueue update helper, config lifecycle, control-thread lifecycle, and connection-loss processing. The header is intentionally small but widely included by the iSNS implementation.
