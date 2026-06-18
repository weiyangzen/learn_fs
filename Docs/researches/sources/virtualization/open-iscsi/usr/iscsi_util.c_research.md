# File Research: sources/virtualization/open-iscsi/usr/iscsi_util.c

## Purpose
`iscsi_util.c` contains shared process, socket, parsing, config, address, session-matching, and kernel-prctl helpers used by `iscsid`, `iscsiadm`, `iscsistart`, and IPC code.

## Main APIs
- `setup_abstract_addr()` builds an abstract AF_LOCAL `sockaddr_un` from a namespace string and returns the correct address length.
- `daemon_init()` redirects stdio to `/dev/null`, creates a new session, changes directory to `/`, and closes the opened null descriptor.
- `oom_adjust()` best-effort raises process priority and lowers OOM killer score through `/proc/self/oom_score_adj` or legacy `/proc/self/oom_adj`.
- `str_to_ipport()` parses portal strings into IP/hostname, port, and TPGT, including IPv6 bracket handling and comma-separated TPGT.
- `increase_max_files()` raises `RLIMIT_NOFILE` to at least `16384`.
- `strstrip()` trims leading and trailing whitespace in place.
- `cfg_get_string_param()` reads a simple `key=value` from a config file, ignoring lines where `#` appears before the key.
- `iscsi_addr_match()` compares addresses directly and, if needed, resolves both sides with `getaddrinfo()` to match DNS names to IP addresses.
- `__iscsi_match_session()` implements common node/session matching on sid, target name, address, port, and iface; wrappers adapt it for session callbacks and target-only matching.
- `set_thread_io_flusher()` toggles Linux `PR_SET_IO_FLUSHER`, suppressing logs for unsupported-kernel `EINVAL`.

## Integration Notes
The session matching functions encode the callback semantics used by `iscsi_sysfs_for_each_session()`: some wrappers return positive for match, while `iscsi_match_session_count()` returns `0` for match and `-1` for no-match to fit iterator expectations.

## Risk Notes
- `str_to_ipport()` mutates the input string by inserting NUL terminators.
- `cfg_get_string_param()` uses substring matching for the key before finding `=`, so callers should pass precise keys and config files should avoid ambiguous key names.
- `iscsi_addr_match()` may perform DNS lookups in match paths and logs connection-style debug messages on resolver failure.
