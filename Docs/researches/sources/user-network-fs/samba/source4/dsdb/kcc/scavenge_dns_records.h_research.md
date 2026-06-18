# sources/user-network-fs/samba/source4/dsdb/kcc/scavenge_dns_records.h

Purpose: declares the DNS scavenging entry points used by the KCC service and Python DSDB bindings.

Important APIs: `dns_tombstone_records(TALLOC_CTX *, struct ldb_context *, char **error_string)` tombstones expired dynamic DNS records across AD-integrated zones. `dns_delete_tombstones(...)` deletes tombstoned DNS nodes past the tombstone interval. `remove_expired_records(...)` is declared but not implemented in the paired source file in this subset, so callers should verify generated prototypes or other translation units before relying on it.

Control flow/state: the header carries no implementation state; it exposes functions that mutate DSDB DNS nodes and return `NTSTATUS`, with optional human-readable error strings allocated on the supplied talloc context. It includes loadparm, SAMDB, DSDB utility, and DNS server common headers because callers need concrete LDB and zone-related types.

Dependencies/integration: consumed by `kcc_periodic.c` for scheduled maintenance and by `pydsdb.c` for AD DC-only Python methods. Risks include API drift between the stale `remove_expired_records()` declaration and actual implementation, and callers needing to respect error string ownership. Test signals: compile coverage for AD DC and non-AD DC builds, and callers checking `NT_STATUS_IS_OK()` plus error-string fallbacks.
