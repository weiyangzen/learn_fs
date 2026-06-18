# sources/test-tools/syzkaller/executor/common_bsd.h

Purpose: This shared syzkaller header supplies BSD and Darwin platform support for executor/csource builds, including USB setup on NetBSD, fault injection on NetBSD, tun/tap network injection, TCP resource extraction, and setuid/none sandbox entry.

Important APIs and types: NetBSD-specific APIs include `setup_usb`, `setup_fault`, `inject_fault`, and `fault_injected`. Network helpers include `tunfd`, `vsnprintf_check`, `snprintf_check`, `execute_command`, `initialize_tun`, `syz_emit_ethernet`, `read_tun`, `tcp_resources`, and `syz_extract_tcp_res`. Sandbox helpers include `sandbox_common`, `do_sandbox_none`, `wait_for_loop`, and `do_sandbox_setuid`.

Control flow and state: `initialize_tun` derives a tap device/interface from `procid`, recreates or opens it, remaps it to fd 200, configures MAC/IPv4/IPv6 addresses, and seeds ARP/NDP entries using shell commands with an explicit PATH. `syz_emit_ethernet` writes raw packets to `tunfd`; `syz_extract_tcp_res` reads one packet, parses Ethernet plus IPv4/IPv6 TCP headers, and writes adjusted seq/ack values to the caller buffer. `sandbox_common` sets session and resource limits; setuid sandbox forks, drops to `nobody`, and runs `loop`.

Dependencies and integration points: It depends on BSD libc, `ifconfig`, `arp`, `ndp`, tap/tun devices, NetBSD `/dev/fault`, `common_usb_netbsd.h`, executor flags such as `flag_net_injection`, and the common loop from `common.h`.

Risks and test signals: Risks include host command availability, tap driver loading, fd collision assumptions, packet parser truncation, malformed IPv6 extension headers, privilege requirements, and shell command failure behavior. Tests should cover NetBSD fault ioctls, FreeBSD tap module fallback, network injection with multiple `procid` values, TCP extraction for IPv4/IPv6, and setuid sandbox privilege drop.
