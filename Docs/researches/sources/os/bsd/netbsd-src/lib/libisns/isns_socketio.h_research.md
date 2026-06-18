# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.h

Declares the socket abstraction used by libisns. It defines `isns_socket_t` as `int`, an IPv4 server address wrapper `struct isns_srv_addr_s`, and prototypes for create/connect/close/readv/writev helpers.

The header pulls in `<sys/socket.h>` and `<netinet/in.h>`, so consumers get socket address and `iovec`-related declarations through the platform headers.
