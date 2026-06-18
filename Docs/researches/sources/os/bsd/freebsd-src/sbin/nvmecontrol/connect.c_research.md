# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/connect.c

Implements NVMe over Fabrics `connect` and `connect-all` commands.

Key behaviors:
- Supports TCP transport only.
- Parses address, SubNQN, controller ID, HostNQN, queue count, queue size, keep-alive timeout, reconnect delay, controller loss timeout, SQ flow control, and TCP header/data digests.
- `connect` establishes admin and I/O queues to a specific NVM subsystem, generates handoff parameters if needed, and hands queues to the kernel via `nvmf_handoff_host()`.
- `connect-all` connects to a discovery controller, fetches discovery log entries, filters for supported TCP/no-security entries, and connects to each advertised NVM subsystem.
- Hardcodes some association settings such as TCP `maxr2t = 1`.

Research notes:
- This is userland connection bootstrap for kernel-managed NVMe/TCP controllers.
- Unsupported transports, address families, and TCP security modes are skipped or rejected.
