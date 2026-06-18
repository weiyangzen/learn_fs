## sources/test-tools/stress-ng/stress-tun.c

Purpose: Implements the `tun` network/OS stressor, creating transient `/dev/net/tun` interfaces and driving UDP traffic through a TUN or TAP endpoint.

Important APIs/types/functions: `stress_tun_info`, `stress_tun_supported`, and `stress_tun` integrate with stress-ng option parsing (`tun-tap`, `tun-port`), capability checks, network port reservation, and process state transitions. It depends on Linux `if_tun.h`, `ifreq`, `TUNSETIFF`, `TUNSETOWNER`, `TUNSETGROUP`, `TUNSETPERSIST`, and optional TUN ioctl probes.

Control flow: support first requires `CAP_NET_ADMIN` and a readable `/dev/net/tun`. Each loop reserves a randomized port, opens the tun device, creates either TUN or TAP with `IFF_NO_PI`, assigns owner/group, assigns a random `192.168.x.y` address using `SIOCSIFADDR`, forks a child UDP receiver bound to that address/port, and the parent sends up to 64 small datagrams before killing/reaping the child.

State and persistence: device persistence is explicitly disabled with `TUNSETPERSIST`; ports are reserved/released per iteration; file descriptors, child processes, and temporary interface state are cleaned on each path.

Dependencies/integration: uses `core-net`, `core-capabilities`, affinity and scheduler helpers, stress-ng bogo counters, and Linux networking ioctls.

Risks: requires elevated capability and kernel TUN support; random address assignment may fail; port collisions or socket resource pressure can turn into skip/no-resource paths; one suspicious probe uses `TUNSETVNETHDRSZ` after `TUNGETSNDBUF`, likely intentional ioctl exercise but worth reviewing.

Test signals: `VERIFY_ALWAYS`; failures come from ioctl/socket/bind/child exit checks and successful bogo increments after each create/send/reap cycle.
