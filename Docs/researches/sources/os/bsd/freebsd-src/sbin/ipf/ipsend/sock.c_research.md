# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/sock.c

This file provides kernel-memory TCP PCB inspection and a socket-assisted TCP send path.

`kmemcpy()` opens `/dev/kmem`, seeks to a kernel address, and reads bytes into user space. `getproc()` obtains the current process info via `sysctl(KERN_PROC_PID)`.

`find_tcp()` walks the current process file descriptor table, file object, socket, inpcb, and tcpcb through kernel memory to return the kernel TCP PCB pointer for a socket descriptor.

`do_socket()` creates a nonblocking TCP socket, binds it to the requested source, obtains the selected local port, opens the packet output device, finds the TCP PCB, initiates connect, copies TCP state fields, sends a crafted TCP packet, writes “Hello World”, sleeps, and closes.

Important dependencies include kernel headers, `kvm`, process/file/socket structures, TCP PCB structures, and `ipsend.h`.

Implementation notes and risks:
- Extremely kernel ABI dependent and privileged.
- Uses kernel private structures and address reads.
- Memory cleanup in successful `find_tcp()` intentionally leaks temporary allocations because it returns a kernel pointer, not copied object state.
