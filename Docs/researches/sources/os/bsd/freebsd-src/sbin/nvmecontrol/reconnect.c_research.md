# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/reconnect.c

Purpose: Implements `nvmecontrol reconnect` for reconnecting an NVMe-oF controller and handing queues back to the kernel.

Key behavior:
- Registers top-level `reconnect`.
- Supports TCP transport options, Host NQN, keep-alive timeout, reconnect delay, controller-loss timeout, I/O queue count, queue size, SQ flow control, and TCP header/data digests.
- Fetches reconnect parameters from an existing controller via `nvmf_reconnect_params()`.
- Validates reconnect parameter nvlist contents, including discovery log entry size and required TCP digest fields.
- Can reconnect using stored discovery parameters or an explicit replacement address/port.
- Uses libnvmf helpers to connect admin and I/O queues, generate or reuse discovery log handoff data, and call `nvmf_reconnect_host()`.

Dependencies:
- `libnvmf`, `fabrics.h`, FreeBSD nvlist APIs.
- Shared `open_dev()`.

Research notes:
- Only TCP is supported in this implementation.
- In `reconnect_by_params()`, the `tcp_association_params()` call appears unreachable because a `break` exits the TCP case before that setup block. This is worth reviewing if digest/association parameters are not applied during stored-parameter reconnects.
