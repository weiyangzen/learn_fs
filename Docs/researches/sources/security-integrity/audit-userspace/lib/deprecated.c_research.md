# sources/security-integrity/audit-userspace/lib/deprecated.c

Purpose: Holds compatibility APIs that are deprecated but still exported, currently `audit_send_user_message`.

Important API: `audit_send_user_message(int fd, int type, hide_t hide_error, const char *message)` sends a user-space audit message with compatibility error handling.

Control flow: Calls `audit_send` with a NUL-terminated message length. Returns success-like `0` for `-ECONNREFUSED` to tolerate kernels built without audit. Returns `0` for hidden `-EPERM` when the process lacks audit write capability. On `-EINVAL`, retries one time as legacy `AUDIT_USER` for user message types in the first user message range. Otherwise returns the audit send result.

State and persistence: No internal state. Sends audit netlink records when successful.

Dependencies and integration: Depends on `audit_send`, capability helpers, audit record ranges, and `hide_t` from private headers. Used by `audit_logging.c`.

Risks: Compatibility behavior intentionally hides some failures, which is useful for unprivileged applications but can mask audit delivery issues. The fallback to `AUDIT_USER` is limited to older kernels and first-range user messages.

Test signals: Mock `audit_send` results for success, `ECONNREFUSED`, hidden/non-hidden `EPERM`, `EINVAL` retry, and non-user message `EINVAL`.
