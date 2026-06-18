# File Research: sources/virtualization/open-iscsi/usr/iscsi_settings.h

This header defines default initiator settings used by open-iscsi runtime and database setup.

Key defaults:
- Login/logout/noop/replacement timeouts.
- Error-handling timeouts for abort, LU reset, target reset, and host reset.
- Session reopen retry/logging defaults.
- Queue limits: `CMDS_MAX` and `QUEUE_DEPTH`.
- Xmit thread priority default.
- Default iface values:
  - iface name
  - netdev
  - IP address
  - hardware address
  - transport
  - unknown value marker
- Unknown portal group tag sentinel.
- TCP window size.
- Default iSCSI port `3260`.
- Initiator burst/data segment lengths.
- Initial login retry max.
- Initial autoscan enabled flag.

Important dependencies:
- None included directly; it is a pure constants header.

Filesystem/storage relevance:
- These defaults shape login behavior, error recovery, queue depth, TCP behavior, and target scanning for remote block storage sessions.

Notable constraints:
- The file notes that these defaults may differ from RFC values; protocol constants live elsewhere.
- Defaults are consumed across IDBM setup, iface setup, connection initialization, and session recovery.
