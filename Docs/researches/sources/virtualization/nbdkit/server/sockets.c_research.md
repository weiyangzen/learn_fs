# File Research: sources/virtualization/nbdkit/server/sockets.c

This file creates listening sockets and runs the accept loop. It supports Unix sockets, TCP/IP sockets, vsock sockets, and optional SELinux socket creation labels. Socket creation prefers atomic close-on-exec flags and falls back to `set_cloexec` where startup or locking makes that safe.

Unix socket binding validates path length and listens with `SOMAXCONN`. TCP/IP binding uses `getaddrinfo`, defaults to port `10809`, sets `SO_REUSEADDR`, enforces IPv6-only sockets when available, ignores unavailable IPv6 families or address-in-use candidates when alternatives exist, and updates the global port string when `--port=0` lets the kernel choose a port. Vsock binding parses a numeric port and binds `VMADDR_CID_ANY`.

Accepted connections are handled by detached pthreads. Each thread gets thread-local server state, an instance number, then calls `handle_single_connection`. A global mutex/condition counter tracks live connection threads so shutdown can wait for all of them before unloading plugins and closing listeners.

The accept loop polls all listening sockets plus `quit_fd` on POSIX, or uses `WaitForMultipleObjectsEx` on Windows. A readable quit object breaks the loop without accepting more connections. Accepted sockets have `TCP_NODELAY` set opportunistically and `SO_KEEPALIVE` enabled when requested.
