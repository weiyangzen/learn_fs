# sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_reconnect.c

`winbindd_reconnect.c` wraps `msrpc_methods` with one-shot reconnect retry behavior and exposes the wrapper as `reconnect_methods`. Its purpose is to centralize the decision about which NTSTATUS failures indicate a broken connection rather than a real lookup/authz result.

`reconnect_need_retry()` returns false for success, warning/non-error statuses, and expected semantic failures such as `NONE_MAPPED`, `NO_SUCH_USER`, `NO_SUCH_GROUP`, `NO_SUCH_ALIAS`, `NO_SUCH_MEMBER`, `NO_SUCH_DOMAIN`, `NO_SUCH_PRIVILEGE`, and `NO_MEMORY`. For other NTSTATUS errors it calls `reset_cm_connection_on_error(domain, NULL, status)` and returns true. Each wrapper method calls the corresponding `msrpc_methods` function once, retries once if `reconnect_need_retry()` says to, and returns the second result if retried.

The wrapped APIs cover user listing, domain/local group enumeration, name-to-SID, SID-to-name, RIDs-to-names, user groups, user aliases, alias members, group members, lockout policy, password policy, and trusted domains. There is no file-local persistence, but retry behavior mutates connection-manager state by resetting bad connections and may force a fresh RPC bind on the second call.

Dependencies include `msrpc_methods`, `struct winbindd_methods`, NTSTATUS helpers, and connection manager reset behavior. Integration points are domain backend selection: domains can use `reconnect_methods` instead of raw `msrpc_methods` to improve resilience to stale/broken pipes. Risks include retrying non-idempotent operations if new methods are added without care, masking the first failure, not retrying some transport-like statuses listed as semantic failures, and added latency on hard failures. Test signals include simulated broken SAMR/LSA pipes, expected no-retry semantic lookup failures, one retry success after connection reset, policy/trusted-domain retry, and method-table completeness compared with `msrpc_methods`.
