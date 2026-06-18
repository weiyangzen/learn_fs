# sources/test-tools/strace/bundled/linux/include/uapi/linux/qrtr.h

## Purpose

Defines the userspace socket address and control packet ABI for Qualcomm IPC Router sockets. strace uses this to decode `AF_QIPCRTR`/QRTR socket addresses and control messages.

## Important APIs, Types, and Dependencies

The header includes `linux/socket.h` for `__kernel_sa_family_t` and `linux/types.h`. `QRTR_NODE_BCAST` and `QRTR_PORT_CTRL` define broadcast and control endpoints. `struct sockaddr_qrtr` contains family, node, and port. `enum qrtr_pkt_type` names data and control commands such as HELLO, BYE, NEW_SERVER, DEL_SERVER, DEL_CLIENT, RESUME_TX, EXIT, PING, NEW_LOOKUP, and DEL_LOOKUP. `struct qrtr_ctrl_pkt` is a packed little-endian command with either server or client payload.

## Control Flow, State, and Integration

The header has no functions. Runtime flow is datagram socket exchange between QRTR nodes and ports, with control packets advertising or removing services and clients. State is network/service discovery state held by the QRTR subsystem and peers.

## Risks and Test Signals

Risks are endian mistakes in packed control packets, confusing node broadcast with a normal node id, and assuming the union payload is valid for every command. Test signals include sockaddr decode tests, named packet type output, and raw fallback for unknown commands.
