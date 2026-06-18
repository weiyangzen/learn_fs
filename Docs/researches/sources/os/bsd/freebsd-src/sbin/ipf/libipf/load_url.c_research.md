# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_url.c

Dispatcher for address-list loading by URL/path scheme.

Key behavior:
- Sends `file://` inputs to `load_file()`.
- Sends absolute or relative local paths to `load_file()`.
- Sends `http://` inputs to `load_http()`.

Research notes:
- `load_file()` opens `filename + 7`, so the plain path branches look inconsistent and likely skip the first seven path characters.
