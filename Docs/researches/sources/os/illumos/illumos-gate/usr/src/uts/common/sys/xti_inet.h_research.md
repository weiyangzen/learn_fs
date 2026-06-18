# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/xti_inet.h

`xti_inet.h` defines Internet-specific XTI option levels, option names, option structures, and IP TOS helper constants. The file explicitly marks itself private and says applications should include the public `<xti_inet.h>` wrapper instead.

The header preserves legacy non-`T_` constants unless `_XPG5` is defined. These include `INET_TCP`, `TCP_NODELAY`, `TCP_MAXSEG`, `TCP_KEEPALIVE`, `INET_UDP`, `UDP_CHECKSUM`, `INET_IP`, and selected `IP_*` option numbers. Comments explain that some constants are exposed only for XTI specification test assertions or compatibility, and their semantics may follow established `<netinet/in.h>` behavior rather than strict XTI semantics.

The preferred modern constants use the `T_` prefix: `T_INET_TCP`, `T_TCP_NODELAY`, `T_TCP_MAXSEG`, `T_TCP_KEEPALIVE`, `T_INET_UDP`, `T_UDP_CHECKSUM`, `T_INET_IP`, and `T_IP_*` options. `struct t_kpalive` is the XTI TCP keepalive option payload, with on/off and timeout fields using `t_scalar_t`.

For IP type-of-service, the header defines precedence levels from routine through network control and service bits for low delay, high throughput, high reliability, and low cost. `SET_TOS()` combines precedence and service bits into the encoded TOS byte.

This file is primarily ABI compatibility glue between XTI and the Internet protocol option namespaces.
