# sources/security-integrity/audit-userspace/lib/audit_logging.c

Purpose: Implements public helper APIs for formatting and sending common user-space audit records: generic user messages, command messages, account changes, SELinux AVC/user-role changes, and safe audit value encoding.

Important APIs and functions: Public functions include `audit_value_needs_encoding`, `audit_encode_value`, `audit_encode_nv_string`, `audit_log_user_message`, `audit_log_user_comm_message`, `audit_log_acct_message`, `audit_log_user_avc_message`, `audit_log_semanage_message`, and `audit_log_user_command`. Internal helpers resolve hostnames, determine executable path, command name, tty, and local hostname.

Control flow: Encoding helpers decide whether values need hex encoding when they contain quotes, control/space characters, or non-printable bytes. Logging functions assemble bounded `MAX_AUDIT_MESSAGE_LENGTH` records with standard key/value fields, derive missing address/tty/exe/comm/cwd values from the local process, and call `audit_send_user_message`. AVC logging has a special `-EPERM` path that syslogs instead of failing when the process cannot write audit records.

State and persistence: Uses static cached executable-name buffers and a cached hostname. Persistent effects are audit netlink messages and possible syslog fallback/error messages. It reads `/proc/self/exe`, `/proc/self/comm`, tty metadata, current working directory, and resolver state.

Dependencies and integration: Depends on `libaudit.h`, `private.h`, netlink send APIs from libaudit/deprecated path, libc resolver APIs, `/proc`, syslog, and audit record constants. These helpers are exported through `audit_logging.h` and included by `libaudit.h`.

Risks: Logging format is ABI-like because parsers consume key/value fields. Caller-provided strings must be encoded consistently with kernel audit conventions. Static caches are not fully thread-specific. Hostname resolution can block and logs resolver errors. `strncat` into `addrbuf` assumes initialized empty buffer and truncates silently.

Test signals: Unit tests for encoding/quoting, NULL and empty input handling, oversized command trimming, cwd encoding, tty validation, audit send failure handling, and golden audit record strings for each public logging function.
