# File Research: sources/virtualization/open-iscsi/usr/iscsi_util.h

## Purpose
`iscsi_util.h` declares shared utility functions for daemon startup, IPC socket addressing, resource tuning, config parsing, session matching, address matching, and IO flusher control.

## Exports
The header forward-declares `node_rec`, `iface_rec`, `session_info`, and `sockaddr_un`; exports process helpers (`oom_adjust`, `daemon_init`, `increase_max_files`), portal parsing, session matching helpers, `MATCH_ANY_SID`, `strstrip`, `cfg_get_string_param`, `setup_abstract_addr`, `iscsi_addr_match`, and `set_thread_io_flusher`.

## Integration Notes
This is a small cross-cutting header included by daemon, admin, IPC, logging, and sysfs code. Its matching APIs depend on open-iscsi record semantics but avoid including their full definitions.
