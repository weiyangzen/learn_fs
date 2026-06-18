# File Research: sources/os/linux/linux/fs/smb/smbdirect/internal.h

Internal umbrella header for the SMB Direct subsystem. It sets the default symbol namespace, logging prefix, global module state, internal device record type, and cross-file function prototypes.

Contents:
- Defines `DEFAULT_SYMBOL_NAMESPACE "SMBDIRECT"` and `pr_fmt`.
- Includes public `<linux/smbdirect.h>` and local `pdu.h`, then includes `socket.h` after declaring global state.
- Defines `struct smbdirect_module_state` with a mutex, six workqueues (`accept`, `connect`, `idle`, `refill`, `immediate`, `cleanup`), and the global RDMA device list.
- Declares `extern struct smbdirect_module_state smbdirect_globals`.
- Defines `struct smbdirect_device` for tracked IB devices.
- Declares internal socket initialization, cleanup scheduling, QP/mempool, send/recv, reassembly, negotiation, MR-list, accept, and device init/exit functions.
- Provides cleanup scheduling macros:
  - `smbdirect_socket_schedule_cleanup()`
  - `smbdirect_socket_schedule_cleanup_lvl()`
  - `smbdirect_socket_schedule_cleanup_status()`

Important role:
- This header is the dependency hub for all `fs/smb/smbdirect/*.c` files. It keeps implementation-private lifecycle APIs out of the public SMB Direct header while making them available across subsystem compilation units.

Maintenance notes:
- Because `socket.h` depends on `smbdirect_globals`, the include order in this file is intentional.
- Cleanup scheduling macros capture caller function and line; preserving that behavior is useful for debugging asynchronous disconnects.
