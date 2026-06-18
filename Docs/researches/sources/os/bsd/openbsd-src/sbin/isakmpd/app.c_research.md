# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/app.c

This file is the application-interface wrapper for `isakmpd`.

Key responsibilities:
- Opens the daemon’s PF_KEY application channel unless disabled.
- Dispatches application events to the PF_KEY v2 handler.

Important symbols:
- `int app_socket`: global application socket descriptor.
- `int app_none`: disables application setup when nonzero.
- `app_init()`: opens the monitored PF_KEY v2 connection via `monitor_pf_key_v2_open`.
- `app_handler()`: calls `pf_key_v2_handler(app_socket)`.

Dependencies:
- `monitor.h` for monitored PF_KEY socket opening.
- `pf_key_v2.h` for PF_KEY application handling.
- `log.h` for fatal logging.

Research notes:
- The file intentionally acts as a thin wrapper around one system-dependent application backend.
