# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor.c

Privilege-separation monitor implementation.

`monitor_init()` creates a socketpair, forks, chroots and drops the child to `_isakmpd`, and leaves the parent as a privileged broker. The unprivileged side requests privileged operations by writing command codes and arguments over the socket, sometimes passing or receiving file descriptors.

Brokered operations include opening PF_KEY sockets, opening/statting/fopening approved files, setting selected socket options, binding sockets to allowed ports, and enumerating readable regular/symlink files in approved directories. The privileged side validates file paths against `/var/run/` or read-only `ISAKMPD_ROOT`, validates socket option levels/names, and restricts binds to AF_INET/AF_INET6 with matching lengths and either port 500 or non-privileged ports.

The monitor also owns child signal forwarding, shutdown cleanup of FIFO/PID files, reliable must-read/must-write helpers based on atomicio-style loops, and fd-passing integration through `mm_send_fd()`/`mm_receive_fd()`.
