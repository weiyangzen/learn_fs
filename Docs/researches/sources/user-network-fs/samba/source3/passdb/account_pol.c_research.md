# sources/user-network-fs/samba/source3/passdb/account_pol.c

Purpose: manages Samba account policy metadata and persistent policy values in `account_policy.tdb`, with short-lived gencache support for LDAP-backed policy reads.

Important APIs and flow: `account_policy_names` maps policy enum values to smb.conf-style names, defaults, descriptions, and LDAP attributes. Lookup helpers expose names, descriptions, defaults, and LDAP attrs. `init_account_policy()` opens or creates the TDB, checks `INFO/version`, runs a transaction to upgrade defaults and seed privilege accounts, and grants all privileges to BUILTIN Administrators when enabled. `account_policy_get()` and `account_policy_set()` fetch/store uint32 values. Cache helpers write/read `ACCT_POL/<name>` values with a 60-second TTL.

State and persistence: static `db` is a process-global dbwrap context. Durable state lives in `state_path("account_policy.tdb")`; cache state lives in gencache and expires after `AP_TTL`.

Dependencies and integration: passdb policy enums, dbwrap, privilege initialization, global SIDs, `lp_enable_privileges()`, gencache, and Samba string-to-integer parsing.

Risks: global db lifetime is lazy and long-lived. Upgrade transaction mixes policy initialization and privilege creation, so failures must cancel cleanly. Default value `(uint32_t)-1` represents never/disabled for some policies and must be interpreted consistently by callers. Cache serialization uses decimal text and must reject parse errors.

Test signals: fresh DB creation, version upgrade/race path, invalid policy enum handling, get/set transaction behavior, cache expiry and parse failure, and privilege seeding with privileges enabled/disabled.
