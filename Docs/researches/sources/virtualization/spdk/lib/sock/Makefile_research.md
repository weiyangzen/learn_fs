# File Research: sources/virtualization/spdk/lib/sock/Makefile

This Makefile builds the SPDK `sock` shared library.

It sets `SPDK_ROOT_DIR`, includes the common SPDK make rules, declares shared object version `14.0`, compiles `sock.c` and `sock_rpc.c`, names the library `sock`, enables `-Wpointer-arith`, points `SPDK_MAP_FILE` at `spdk_sock.map`, and includes `spdk.lib.mk`.

The build unit therefore contains the transport-independent socket facade plus its JSON-RPC configuration interface. ABI/export control is delegated to the map file.
