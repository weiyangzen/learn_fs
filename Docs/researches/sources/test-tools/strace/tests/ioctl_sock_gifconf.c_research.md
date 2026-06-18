<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock_gifconf.c -->
# sources/test-tools/strace/tests/ioctl_sock_gifconf.c

Purpose: focused test for `SIOCGIFCONF` decoding of `struct ifconf` and returned `struct ifreq` arrays.

Important APIs/types/functions: Uses `socket`, `ioctl`, `struct ifconf`, `struct ifreq`, `sockaddr_in`, `SIOCGIFCONF`, `print_ifc_len`, and `print_ifconf`. `MAX_STRLEN` is set to 1 to force compact array output.

Control flow: opens an AF_INET socket, allocates an ifconf and buffers, probes NULL and bad pointers, calls `SIOCGIFCONF` with zero/positive lengths and NULL/non-NULL buffers, and prints length changes plus decoded first interface address entries when the call succeeds.

State and persistence behavior: reads interface configuration only; local buffers hold kernel output. No network configuration is modified.

Dependencies/integration points: depends on available AF_INET socket, network interfaces, and strace `ifconf` array decoder.

Risks and test signals: output may vary by interface set, but expected harness constrains printed length/count. Passing output confirms `ifc_len` before/after handling, NULL buffer behavior, array truncation, and sockaddr decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock_gifconf.c -->
