# sources/test-tools/strace/bundled/linux/include/uapi/linux/vm_sockets.h

## Purpose
Defines the Linux AF_VSOCK userspace ABI for virtual-machine sockets, including socket options, well-known context IDs, address structure layout, local-CID ioctl, and zerocopy error-queue control-message constants.

## Important APIs, Types, and Functions
Read coverage: 211 lines and 7428 bytes. The header exports `SO_VM_SOCKETS_BUFFER_SIZE`, minimum/maximum buffer socket options, peer host VM ID, trust, nonblocking TX/RX, and old/new connect-timeout option numbers. `SO_VM_SOCKETS_CONNECT_TIMEOUT` is selected with ABI-aware logic based on word size, x32, and `time_t` versus `__kernel_long_t`. Addressing constants include `VMADDR_CID_ANY`, `VMADDR_PORT_ANY`, `VMADDR_CID_HYPERVISOR`, `VMADDR_CID_LOCAL`, `VMADDR_CID_HOST`, and `VMADDR_FLAG_TO_HOST`. Version helpers split epoch, major, and minor from a packed version integer. `struct sockaddr_vm` defines the AF_VSOCK socket address with family, port, CID, flags, and zero padding sized to match `struct sockaddr`. `IOCTL_VM_SOCKETS_GET_LOCAL_CID` returns the local CID. `SOL_VSOCK` and `VSOCK_RECVERR` identify zerocopy completion notifications on the error queue.

## Control Flow
Userspace creates an `AF_VSOCK` socket, optionally adjusts stream-buffer options with `setsockopt`, binds to a CID/port or wildcard address, connects to host, hypervisor, local, or guest CIDs, and can use `VMADDR_FLAG_TO_HOST` to force host forwarding for sibling/nested VM use cases. Code that needs its local address can issue `IOCTL_VM_SOCKETS_GET_LOCAL_CID`. MSG_ZEROCOPY senders receive completion notifications through control messages using `SOL_VSOCK` and `VSOCK_RECVERR`.

## State and Persistence Behavior
No persistent storage is defined. Runtime state is kernel socket state: buffer sizes, connect timeout, trust/nonblocking metadata, selected local and peer CID/port, routing flag, and error-queue notifications. The address struct's fixed size and padding are ABI state that user and kernel code must preserve.

## Dependencies and Integration Points
Direct includes are `<sys/socket.h>`, `<linux/socket.h>`, and `<linux/types.h>`. In strace the constants feed socket option, ioctl, address-family, and control-message decoding. System integration points include VMCI, virtio-vsock, Hyper-V vsock transports, host/guest services, nested VM routing, and zerocopy networking notification handling.

## Risks and Edge Cases
The connect-timeout compatibility macro is time64-sensitive and differs for x32 and 32-bit ABIs. `struct sockaddr_vm` deliberately matches `struct sockaddr`; changing padding or family type would break ABI and strace decoding. CID values use unsigned `-1U` wildcards and low reserved IDs, so decoders must avoid treating them as normal signed negative addresses. `VMADDR_FLAG_TO_HOST` only affects specific routing scenarios, and zerocopy notifications are encoded as standard socket extended errors.

## Test Signals
Compile tests should cover 32-bit, 64-bit, and x32 timeout macro selection. Runtime tests should exercise bind/connect with wildcard, host, local, and hypervisor CIDs, `GET_LOCAL_CID`, buffer option get/set clamping, `VMADDR_FLAG_TO_HOST` routing where supported, zerocopy error-queue messages, and strace output for AF_VSOCK sockaddr and socket options.
