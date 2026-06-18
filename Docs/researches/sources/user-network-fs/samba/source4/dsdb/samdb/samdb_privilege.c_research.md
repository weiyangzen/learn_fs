# sources/user-network-fs/samba/source4/dsdb/samdb/samdb_privilege.c

## Purpose
`samdb_privilege.c` loads local privilege and right assignments from Samba's `privilege.ldb` and applies them to a `security_token`.

## Important APIs, Types, and Functions
`privilege_connect` opens `privilege.ldb`. `samdb_privilege_setup_sid` searches privilege records for one SID and applies `privilege` values to a token. `samdb_privilege_setup` handles token-level shortcuts and iterates over all token SIDs.

## Control Flow and Behavior
System, anonymous, and NULL-SID-list tokens are handled without database access. Otherwise the function opens `privilege.ldb`, clears the token privilege mask, then searches each SID as LDAP-encoded NDR `objectSid`. Known privilege names are mapped with `sec_privilege_id`; unknown privilege strings are attempted as rights via `sec_right_bit`, with a debug warning for unrecognized zero mappings.

## State and Persistence Behavior
The persistent source of truth is `privilege.ldb`. The only mutated runtime state is the token's privilege/right bitmask. The database context and search allocations are temporary and freed before return.

## Dependencies and Integration Points
It depends on `ldb_wrap_connect`, generic DB search helpers, LDAP NDR SID encoding, security privilege/right mapping, and loadparm. It is called by `security_token_create` when simple privileges are not requested.

## Risks and Edge Cases
Failure to open `privilege.ldb` returns `NT_STATUS_INTERNAL_DB_CORRUPTION`, which can block token creation. Search results other than exactly one record are treated as no assignment, so duplicate privilege records are silently ignored. Unknown strings can map to right bit zero and only log a warning. Builtin Administrators does not get an unconditional shortcut here; that shortcut exists in the simple-privileges path in `samdb.c`.

## Test Signals
Tests should cover system/anonymous/no-SID shortcuts, missing privilege DB, SID with no record, SID with known privileges, SID with right names, unknown privilege strings, duplicate records, and tokens with multiple SIDs accumulating masks.
