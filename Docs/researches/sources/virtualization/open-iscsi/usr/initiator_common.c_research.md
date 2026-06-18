# File Research: sources/virtualization/open-iscsi/usr/initiator_common.c

This file contains setup logic shared by normal and discovery sessions: session lookup, authentication setup, negotiated parameter validation/copying, portal resolution, host/session/kernel parameter publication, and iface network setup.

Major responsibilities:
- `session_find_by_sid()` searches all transports and sessions for a given SID.
- `iscsi_setup_authentication()` copies CHAP credentials and configures one-way or bidirectional auth buffers.
- `iscsi_copy_operational_params()` validates and copies negotiated session/connection parameters from config into runtime session/connection state.
- `iscsi_setup_portal()` resolves target address/port into `sockaddr_storage`, stores failback address, and records numeric host string.
- `iscsi_host_set_params()` publishes netdev and hardware address host parameters through `ipc->set_host_param`.
- `iscsi_session_init_params()` builds a parameter mask based on transport capabilities, clearing unsupported MaxR2T, digest, and marker parameters.
- `iscsi_session_set_neg_params()` publishes negotiated full-feature iSCSI parameters through `ipc->set_param`.
- `iscsi_session_set_params()` publishes target/session/recovery/auth/NOP/iface/boot/discovery parameters through `ipc->set_param`.
- `iscsi_set_net_config()` invokes transport-specific network configuration setup, deriving host number and netdev when needed.
- `iscsi_host_set_net_params()` enforces/offers iface IP setup, brings up netdevs, applies transport net config, and publishes IP/netdev/hwaddress host parameters.

Important validation behavior:
- Data segment and burst lengths are aligned down to 32-bit boundaries and clamped to allowed min/max values.
- FirstBurstLength is forced to be no larger than MaxBurstLength.
- Discovery sessions cap receive segment length for text negotiation and disable header/data digests.
- NOP timeout parameters are skipped if sysfs says the session does not support kernel NOP handling.
- CHAP with `authmethod=None` is currently warned as deprecated but still allowed if passwords are configured.

Important dependencies:
- Uses transport capability flags and transport templates.
- Uses global `ipc`.
- Uses sysfs for session NOP support, host lookup, and host info.
- Uses iface and net helpers for binding and netdev setup.

Filesystem/storage relevance:
- This file establishes kernel-visible session parameters for remote storage connections. Incorrect parameter publication can affect login success, error recovery, queueing, and discovery of block devices.

Notable constraints:
- Return codes mix POSIX-style values and open-iscsi error codes depending on caller path.
- Unsupported kernel operations returning `-ENOSYS` are often tolerated for compatibility.
- Some TODOs remain around older kernel handling and initiator-name host fallback.
