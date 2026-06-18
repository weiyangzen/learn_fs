# sources/test-tools/strace/src/sockaddr.c

Purpose: shared socket-address decoder for many Linux address families.

Important APIs/types/functions: `print_sockaddr`, `decode_sockaddr`, `print_inet_addr`, `decode_inet_addr`, per-family printers for UNIX, INET/INET6, AX.25, IPX, X.25, netlink, packet, TIPC, Bluetooth, RxRPC, IEEE 802.15.4, ALG, NFC, VSOCK, QRTR, XDP, and MCTP, plus `sa_printers`.

Control flow: `decode_sockaddr` validates minimum length, copies at most `sockaddr_storage`, zero-pads the local buffer, then calls `print_sockaddr`. `print_sockaddr` prints `sa_family`, dispatches to a family printer only when the family has a registered printer and `addrlen` satisfies that printer's minimum length, otherwise prints raw `sa_data`. Family printers handle byte-order wrappers, nested unions, variable-length arrays, optional tail fields, abstract UNIX names, SELinux file context annotations, and xlat verbosity.

State and persistence behavior: stateless except local static buffers in address-to-string helpers. All tracee memory is copied into a bounded local storage buffer before decoding.

Dependencies and integration points: heavily used by socket syscalls and `sock.c`; depends on many Linux protocol headers, xlat tables, netlink constants, SELinux context hooks, MAC/hardware address printers, and xlat verbosity policy.

Risks: address-family structs evolve and may be shorter than current headers; min-length guards and raw fallback protect output but can miss newer fields. Bluetooth endian wrappers use host-endian conversion based on `is_bigendian`. UNIX path and SELinux annotation are path-sensitive. Numerous xlat tables make golden output broad.

Test signals: valid and short addresses for every registered family, unknown families, abstract UNIX sockets, IPv4/IPv6 raw/verbose output, AX.25 validity/raw paths, packet hardware address truncation, Bluetooth length variants, NFC 32/64-bit service-name length, XDP shared-UMEM fd, and malformed/truncated buffers.
