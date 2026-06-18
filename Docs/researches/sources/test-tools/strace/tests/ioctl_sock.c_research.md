<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock.c -->
# sources/test-tools/strace/tests/ioctl_sock.c

Purpose: broad socket ioctl decoder test for generic file/socket ownership commands and networking `SIOC*`/`ifreq` commands.

Important APIs/types/functions: Uses `socket(AF_INET, SOCK_STREAM, 0)`, `do_ioctl`, `test_ptr`, `test_int`, `test_str`, `test_ifreq`, `struct ifreq`, `sockaddr_in`, `ifmap`, `FIOGETOWN/FIOSETOWN`, `SIOCGPGRP/SIOCSPGRP`, `SIOCATMARK`, route/ARP/RARP/bridge/bond/VLAN/ethtool/MII/hwtstamp commands, and many `SIOCGIF*`/`SIOCSIF*` variants.

Control flow: opens an AF_INET socket, then `test_ptr` probes NULL and bad pointers for a long command list plus unknown `_IO(0x89, 0xff)`. `test_int` checks int pointer commands on a real socket. `test_str` checks bridge name string truncation. `test_ifreq` builds macro-generated source cases for integer, flag, string, address, hardware address, and map union members, emits EFAULT and structured `ifreq` output, queries loopback ifindex/name, and tests bridge add/delete interface by index.

State and persistence behavior: creates one transient socket and local `ifreq` structs. Set-style ioctls are mostly issued on fd `-1`, avoiding network configuration changes; real socket queries read loopback metadata.

Dependencies/integration points: depends on networking headers, loopback interface assumptions, `IFINDEX_LO_STR`, sockaddr and flag xlat tables, and optional command macros from current headers.

Risks and test signals: command availability and loopback naming/index can vary. Passing output confirms pointer handling, ifreq union member selection, string truncation, sockaddr/hwaddr/map formatting, and interface-index/name decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sock.c -->
