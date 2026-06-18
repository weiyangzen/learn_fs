# sources/test-tools/stress-ng/stress-ping-sock.c

Purpose: `stress-ping-sock.c` implements the `ping-sock` stressor, sending ICMP echo packets over Linux datagram ICMP sockets to loopback while varying payload contents and destination ports.

Important APIs/types/functions: the build requires Linux, `PF_INET`, `SOCK_DGRAM`, `IPPROTO_ICMP`, and `struct icmphdr`. `stress_rawsock_open()` opens `socket(AF_INET, SOCK_DGRAM, IPPROTO_ICMP)` and maps permission/protocol failures to skip/not-implemented. `stress_rawsock_supported()` probes open/close. `stress_ping_sock()` builds and sends packets.

Control flow: the stressor resolves `ping-sock-max-size`, opens the ping socket, initializes a loopback `sockaddr_in`, prepares an ICMP echo header with pid-based id, chooses a starting unprivileged port, synchronizes, and loops. Each iteration fills the payload with a rotating ASCII byte, sends with `sendto()`, records bytes and bogo ops on success, increments ICMP sequence and destination port, and wraps ports back above 1024.

State and persistence behavior: state is a socket fd, stack packet buffer, sockaddr, sequence number, port counter, and metrics. No persistent files or network state are created beyond transient loopback ICMP traffic.

Dependencies and integration points: it integrates with Linux ping-group permissions, stress-ng option parsing, sync barriers, metrics, and `CLASS_NETWORK | CLASS_OS` registration.

Risks: unprivileged ping sockets depend on `/proc/sys/net/ipv4/ping_group_range`; EPERM/EACCES are expected skip conditions. The call uses `ping_sock_max_size` as send length even though the buffer also includes the header, so the configured max size represents total sent bytes from the header start. `sendto()` failures are logged as stressor failures but the loop continues.

Test signals: direct `--ping-sock` should report `ping sendto calls per sec` and `ping bytes per sec`. Permission-denied, unsupported protocol, minimum and maximum size, and loopback-only behavior are the key validation cases.
